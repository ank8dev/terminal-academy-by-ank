"""The blocklist (see LESSONS_PLAN.md, section 4.1).

IMPORTANT: this prevents *accidents*, it is NOT real security. The student
runs commands as their own user, and a determined person can get around any
pattern list (for example with variables or `eval`). The goal is only that a
beginner who copies a scary command from the internet does not hurt their
computer while learning.

Some patterns come from the old desktop app's blacklist.json (reverse shells,
`shred`, firewall flushing, network scanning).
"""

from __future__ import annotations

import os
import re
import shlex
from typing import List, Optional, Sequence

GENERIC = (
    "This command can damage a computer, so it is blocked in Terminal Academy."
)

# A command word starts at the beginning of the line, after ; & | ( { or
# backtick, after $( or after a "wrapper" word like exec, env or xargs.
_START = r"(?:^|[;&|({`]\s*|\$\(\s*|\b(?:exec|env|nohup|time|command|builtin|xargs|nice|then|do|else)\s+)"

# (regex, friendly reason). Checked with re.search on the whole line.
PATTERNS = [
    (_START + r"(sudo|su|doas|pkexec)\b",
     "Terminal Academy never needs admin rights, so sudo, su and doas are "
     "blocked. Everything you need works as a normal user."),
    (_START + r"(shutdown|reboot|halt|poweroff)\b",
     "That would turn off or restart your computer, so it is blocked here."),
    (_START + r"init\s+[06]\b",
     "That would turn off or restart your computer, so it is blocked here."),
    (_START + r"(mkfs\S*|fdisk|sfdisk|gdisk|diskutil|parted|wipefs)\b",
     "Disk tools can erase a whole disk, so they are blocked in Terminal Academy."),
    (_START + r"shred\b",
     "shred destroys files so they can never come back, so it is blocked here."),
    (_START + r"dd\b.*\bof=",
     "dd can overwrite a whole disk with one typo, so writing with dd is "
     "blocked here."),
    (r">\s*/dev/(sd|hd|disk|nvme|mmcblk|vd|xvd)",
     "Writing straight to a disk device can destroy all its data, so it is blocked."),
    (r":\s*\(\s*\)\s*\{",
     "That is a 'fork bomb': it copies itself until the computer freezes. "
     "Blocked, but now you know what it looks like!"),
    (r"\b(curl|wget)\b.*\|\s*(sudo\s+)?(ba|z|da|k|fi)?sh\b",
     "Piping a download straight into a shell runs code from the internet "
     "without reading it first. That is blocked here, and it is a good habit "
     "to avoid it everywhere."),
    (r"\bkill\s+(-\S+\s+)*-1\b",
     "kill -1 stops (almost) every program you are running, so it is blocked. "
     "Use kill with one process id instead."),
    (_START + r"(killall|pkill)\b",
     "killall and pkill can stop many programs at once, so they are blocked "
     "here. Use kill with one process id instead."),
    (_START + r"(systemctl|launchctl|crontab|passwd|chsh|chfn|visudo|usermod|useradd|userdel)\b",
     "That command changes how your computer is set up, so it is blocked in "
     "Terminal Academy."),
    (_START + r"(iptables|ip6tables|nft|ufw|pfctl)\b",
     "Firewall commands can cut your computer off the network, so they are blocked here."),
    (_START + r"(nmap|masscan)\b",
     "Scanning other computers without permission is not OK, so network "
     "scanners are blocked here."),
    (r"/dev/(tcp|udp)/",
     "That opens a hidden network connection (a 'reverse shell'), so it is blocked."),
    (_START + r"(nc|ncat|netcat)\b.*\s-[a-zA-Z]*[ec]\b",
     "That opens a hidden network connection (a 'reverse shell'), so it is blocked."),
    (_START + r"(scp|sftp|telnet|mosh|rlogin)\b",
     "Terminal Academy never connects to other computers, so remote access "
     "commands are blocked. You will learn SSH safely with ssh-keygen and ssh -G."),
]

_COMPILED = [(re.compile(p), r) for p, r in PATTERNS]

# Commands that change files. For these we check that the paths stay inside
# the sandbox. Reading outside is fine (`cat /etc/hosts`).
WRITE_COMMANDS = {
    "rm", "rmdir", "mv", "cp", "touch", "mkdir", "chmod", "chown", "chgrp",
    "ln", "tee", "truncate", "unlink", "install",
}
# For these, only the last path is written (the others are only read).
LAST_ONLY = {"cp", "ln", "install"}
# For these, the first non-option word is not a path (mode or owner).
SKIP_FIRST = {"chmod", "chown", "chgrp"}
WRAPPERS = {"exec", "nohup", "command", "builtin", "time", "nice", "env"}
OPERATORS = {";", "&", "&&", "|", "||", "(", ")", "|&", ";;", "{", "}"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", "<>"}
SAFE_DEVICES = ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty", "/dev/fd/")

OUTSIDE = ("That would change files outside your sandbox, so I did not run it. "
           "Reading files outside is fine; changing them is not.")
RM_HOME = "That would delete your whole sandbox. Use reset instead."
RM_ROOT = ("That would try to delete everything on the computer! It is the most "
           "famous dangerous command, so it is blocked.")
RM_HERE = ("That would delete everything in your sandbox. If you want a fresh "
           "start, type reset instead.")


def _tokenize(command: str) -> Optional[List[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    lexer.commenters = "#"
    try:
        return list(lexer)
    except ValueError:  # unbalanced quotes: bash will complain anyway
        return None


def _split_segments(tokens: Sequence[str]) -> List[List[str]]:
    segments: List[List[str]] = [[]]
    for tok in tokens:
        if tok in OPERATORS:
            segments.append([])
        else:
            segments[-1].append(tok)
    return [s for s in segments if s]


def _strip_prefix(words: List[str]) -> List[str]:
    """Drop NAME=value assignments and wrapper words like nohup/env."""
    words = list(words)
    while words:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            words.pop(0)
        elif words[0] in WRAPPERS:
            words.pop(0)
            while words and words[0].startswith("-"):
                words.pop(0)
        else:
            break
    return words


def _resolve(path: str, sandbox: str, cwd: str) -> Optional[str]:
    """Absolute, normalized path; None if we cannot tell (e.g. $VAR)."""
    for home in ("$HOME", "${HOME}"):
        if path == home or path.startswith(home + "/"):
            path = "~" + path[len(home):]
    if path == "~" or path.startswith("~/"):
        path = sandbox + path[1:]
    elif path.startswith("~"):
        return None  # ~otheruser: unknown
    if "$" in path or "`" in path:
        return None
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    # realpath resolves the parts that exist (and symlinks pointing outside).
    return os.path.realpath(path)


def _inside(path: str, sandbox: str) -> bool:
    root = os.path.realpath(sandbox)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _check_rm(words: List[str], sandbox: Optional[str], cwd: Optional[str]) -> Optional[str]:
    flags = [w for w in words[1:] if w.startswith("-") and w != "-"]
    recursive = any(
        f in ("--recursive",) or (not f.startswith("--") and ("r" in f or "R" in f))
        for f in flags
    )
    if not recursive:
        return None
    targets = [w for w in words[1:] if not w.startswith("-")]
    at_root = (
        sandbox is not None
        and cwd is not None
        and os.path.realpath(cwd) == os.path.realpath(sandbox)
    )
    for t in targets:
        clean = t.rstrip("/") or "/"
        if clean in ("/", "/*") or t.startswith("/*"):
            return RM_ROOT
        if clean in ("~", "$HOME", "${HOME}", "~/*", "$HOME/*", "${HOME}/*"):
            return RM_HOME
        if clean in (".", "..", "./*", "../*"):
            return RM_HERE
        if clean in ("*", ".*") and at_root:
            return RM_HERE
    return None


def _check_paths(words: List[str], sandbox: str, cwd: str) -> Optional[str]:
    name = os.path.basename(words[0])
    if name not in WRITE_COMMANDS:
        return None
    args = []
    after_dashdash = False
    for w in words[1:]:
        if not after_dashdash and w == "--":
            after_dashdash = True
            continue
        if not after_dashdash and w.startswith("-") and w != "-":
            continue
        args.append(w)
    if name in SKIP_FIRST:
        args = args[1:]
    if name in LAST_ONLY:
        args = args[-1:]
    for arg in args:
        resolved = _resolve(arg, sandbox, cwd)
        if resolved is not None and not _inside(resolved, sandbox):
            return OUTSIDE
    return None


def _check_redirects(tokens: Sequence[str], sandbox: str, cwd: str) -> Optional[str]:
    for i, tok in enumerate(tokens[:-1]):
        if tok not in REDIRECTS:
            continue
        target = tokens[i + 1]
        if target.startswith(SAFE_DEVICES):
            continue
        resolved = _resolve(target, sandbox, cwd)
        if resolved is not None and not _inside(resolved, sandbox):
            return OUTSIDE
    return None


def _check_ssh(words: List[str]) -> Optional[str]:
    if os.path.basename(words[0]) != "ssh":
        return None
    if any(w in ("-G", "-V") or (w.startswith("-") and not w.startswith("--")
                                 and ("G" in w[1:] or "V" in w[1:]))
           for w in words[1:]):
        return None
    if len(words) == 1:
        return None  # plain `ssh` only prints the usage text
    return ("Terminal Academy never connects to other computers, so ssh to a "
            "server is blocked. ssh -G (show settings) and ssh-keygen are allowed.")


def check_command(
    command: str, sandbox: Optional[str] = None, cwd: Optional[str] = None
) -> Optional[str]:
    """Return a friendly reason if ``command`` is blocked, else None.

    ``sandbox`` and ``cwd`` enable the "do not change files outside the
    sandbox" checks; without them only the patterns are checked.
    """
    line = command.strip()
    if not line:
        return None
    for regex, reason in _COMPILED:
        if regex.search(line):
            return reason

    tokens = _tokenize(line)
    if tokens is None:
        return None
    if sandbox is not None and cwd is None:
        cwd = sandbox
    for segment in _split_segments(tokens):
        words = _strip_prefix(segment)
        # Redirections are not part of the command's arguments.
        plain: List[str] = []
        skip = False
        for w in words:
            if skip:
                skip = False
                continue
            if w in REDIRECTS or w in ("<", "<<", "<<<", ">&", "<&"):
                skip = True
                continue
            plain.append(w)
        if not plain:
            continue
        name = os.path.basename(plain[0])
        if name == "rm":
            reason = _check_rm(plain, sandbox, cwd)
            if reason:
                return reason
        reason = _check_ssh(plain)
        if reason:
            return reason
        if sandbox is not None and cwd is not None:
            reason = _check_paths(plain, sandbox, cwd)
            if reason:
                return reason
    if sandbox is not None and cwd is not None:
        return _check_redirects(tokens, sandbox, cwd)
    return None
