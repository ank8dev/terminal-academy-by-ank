"""Run the student's commands (see LESSONS_PLAN.md, section 2.9).

Every command runs in a new ``bash -c`` (or ``sh -c``) process. A small wrapper
script loads the saved environment and current folder first, and saves them
again afterwards, so ``cd`` and ``export`` "stick" between commands.

Captured commands write stdout/stderr to temp files (not pipes, so a
background job like ``sleep 300 &`` cannot make us wait forever), read
``/dev/null`` as stdin and run in their own process group. We remember those
groups and stop them in ``cleanup()``.
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

# Programs that need the real terminal (keyboard and screen).
INTERACTIVE = frozenset(
    ["less", "more", "man", "nano", "vi", "vim", "top", "htop", "clear"]
)

DEFAULT_TIMEOUT = 30.0
KILL_GRACE = 2.0
# Show at most this much output per stream (a runaway `yes` can print a lot).
MAX_SHOWN_BYTES = 200_000
# Files bigger than this cannot be written by student commands (protects the
# disk against `yes > file` and similar accidents).
MAX_FILE_BYTES = 100 * 1024 * 1024

# The wrapper. The student command is passed in an environment variable and
# run with `eval`, so a syntax error or a `#` comment in it cannot break the
# wrapper. The EXIT trap saves the folder and environment even after `exit`.
WRAPPER = r"""
__ta_state=$TA_STATE
__ta_cmd=$TA_CMD
__ta_cwd=$TA_CWD
unset TA_STATE TA_CMD TA_CWD
if [ -f "$__ta_state/env.sh" ]; then
  . "$__ta_state/env.sh" 2>/dev/null
fi
__ta_save() {
  __ta_rc=$?
  pwd > "$__ta_state/cwd.tmp" 2>/dev/null && mv -f "$__ta_state/cwd.tmp" "$__ta_state/cwd"
  export -p > "$__ta_state/env.tmp" 2>/dev/null && mv -f "$__ta_state/env.tmp" "$__ta_state/env.sh"
  exit $__ta_rc
}
trap __ta_save EXIT
cd "$__ta_cwd" || exit 1
eval "$__ta_cmd"
"""


@dataclass
class Result:
    """What happened when a command ran."""

    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    cwd: str = ""
    timed_out: bool = False
    interrupted: bool = False
    moved_back: bool = False
    interactive: bool = False
    truncated: bool = False


def find_shell() -> str:
    return shutil.which("bash") or shutil.which("sh") or "/bin/sh"


def _segments_first_words(command: str) -> List[str]:
    """First word of every part of a command line (split at | ; & && ||)."""
    words = []
    for part in re.split(r"\|\|?|&&?|;", command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        # Skip leading NAME=value assignments.
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens.pop(0)
        if tokens:
            words.append(os.path.basename(tokens[0]))
    return words


def is_interactive(command: str) -> bool:
    return any(w in INTERACTIVE for w in _segments_first_words(command))


def _within(path: str, root: str) -> bool:
    path = os.path.realpath(path)
    root = os.path.realpath(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _limit_resources() -> None:  # runs in the child, before exec
    os.setpgrp()
    try:
        import resource

        soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
        limit = MAX_FILE_BYTES
        if hard != resource.RLIM_INFINITY:
            limit = min(limit, hard)
        resource.setrlimit(resource.RLIMIT_FSIZE, (limit, hard))
    except (ImportError, ValueError, OSError):
        pass


def _read_limited(fh) -> Tuple[str, bool]:
    fh.seek(0)
    data = fh.read(MAX_SHOWN_BYTES + 1)
    truncated = len(data) > MAX_SHOWN_BYTES
    return data[:MAX_SHOWN_BYTES].decode("utf-8", errors="replace"), truncated


class Shell:
    """Runs commands for one lesson sandbox.

    ``sandbox`` is the lesson's practice folder (also used as ``HOME``),
    ``state_dir`` holds the saved folder and environment between commands.
    """

    def __init__(
        self,
        sandbox: str,
        state_dir: str,
        timeout: float = DEFAULT_TIMEOUT,
        use_tty: Optional[bool] = None,
        shell: Optional[str] = None,
    ) -> None:
        self.sandbox = os.path.realpath(sandbox)
        self.state_dir = os.path.abspath(state_dir)
        self.timeout = timeout
        self.shell = shell or find_shell()
        if use_tty is None:
            use_tty = _isatty(sys.stdin) and _isatty(sys.stdout)
        self.use_tty = use_tty
        self.pgids: Set[int] = set()
        os.makedirs(self.state_dir, exist_ok=True)
        self.cwd = self._load_cwd()

    # ----- state ----------------------------------------------------------

    def _load_cwd(self) -> str:
        try:
            with open(os.path.join(self.state_dir, "cwd"), encoding="utf-8") as fh:
                cwd = fh.read().strip()
        except OSError:
            return self.sandbox
        if cwd and os.path.isdir(cwd) and _within(cwd, self.sandbox):
            return os.path.realpath(cwd)
        return self.sandbox

    def reset_state(self) -> None:
        """Forget the saved folder and environment (used by `reset`)."""
        for name in ("cwd", "env.sh", "cwd.tmp", "env.tmp"):
            try:
                os.remove(os.path.join(self.state_dir, name))
            except OSError:
                pass
        self.cwd = self.sandbox

    def relative_cwd(self) -> str:
        """The current folder as the prompt shows it, e.g. ``~/school/math``."""
        rel = os.path.relpath(self.cwd, self.sandbox)
        return "~" if rel == "." else "~/" + rel

    def _env(self) -> dict:
        env_file = os.path.join(self.state_dir, "env.sh")
        if os.path.isfile(env_file):
            # The saved environment has every exported variable, so start
            # almost empty: then `unset NAME` sticks too.
            env = {"PATH": os.environ.get("PATH", os.defpath)}
            for key in ("TERM", "LANG", "LC_ALL", "LC_CTYPE", "COLUMNS", "LINES"):
                if key in os.environ:
                    env[key] = os.environ[key]
        else:
            env = dict(os.environ)
            env["HOME"] = self.sandbox
            env["LC_COLLATE"] = "C"  # same `sort` order everywhere
            env.pop("CDPATH", None)
            env.pop("BASH_ENV", None)
            env.pop("ENV", None)
            for key in [k for k in env if k.startswith("TA_")]:
                del env[key]
        env["HOME"] = env.get("HOME", self.sandbox)
        return env

    # ----- running --------------------------------------------------------

    def run(self, command: str, interactive: Optional[bool] = None) -> Result:
        """Run one command line and return what happened."""
        self.prune()
        moved_back = False
        if not os.path.isdir(self.cwd) or not _within(self.cwd, self.sandbox):
            self.cwd = self.sandbox
            moved_back = True
        os.makedirs(self.sandbox, exist_ok=True)

        env = self._env()
        env["TA_STATE"] = self.state_dir
        env["TA_CMD"] = command
        env["TA_CWD"] = self.cwd
        cwd_file = os.path.join(self.state_dir, "cwd")
        try:
            os.remove(cwd_file)
        except OSError:
            pass

        if interactive is None:
            interactive = self.use_tty and is_interactive(command)

        if interactive:
            result = self._run_attached(env)
        else:
            result = self._run_captured(env)

        new_cwd = self._load_cwd_raw(cwd_file)
        if new_cwd is not None:
            if os.path.isdir(new_cwd) and _within(new_cwd, self.sandbox):
                self.cwd = os.path.realpath(new_cwd)
            else:
                self.cwd = self.sandbox
                moved_back = True
                try:
                    with open(cwd_file, "w", encoding="utf-8") as fh:
                        fh.write(self.sandbox + "\n")
                except OSError:
                    pass
        result.cwd = self.cwd
        result.moved_back = moved_back
        return result

    @staticmethod
    def _load_cwd_raw(path: str) -> Optional[str]:
        try:
            with open(path, encoding="utf-8") as fh:
                return fh.read().strip() or None
        except OSError:
            return None

    def _run_attached(self, env: dict) -> Result:
        """Run with the real terminal (for less, man, nano, ...)."""
        proc = subprocess.Popen([self.shell, "-c", WRAPPER], cwd=self.sandbox, env=env)
        while True:
            try:
                rc = proc.wait()
                break
            except KeyboardInterrupt:
                # Ctrl+C goes to the program too; it decides what to do.
                continue
        return Result(returncode=rc, interactive=True)

    def _run_captured(self, env: dict) -> Result:
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            proc = subprocess.Popen(
                [self.shell, "-c", WRAPPER],
                cwd=self.sandbox,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=err,
                preexec_fn=_limit_resources,
            )
            pgid = proc.pid
            self.pgids.add(pgid)
            timed_out = interrupted = False
            try:
                proc.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                self._stop_group(pgid, proc, signal.SIGTERM)
            except KeyboardInterrupt:
                interrupted = True
                self._stop_group(pgid, proc, signal.SIGINT)
            rc = proc.returncode if proc.returncode is not None else -1
            if not _group_alive(pgid):
                self.pgids.discard(pgid)
            stdout, t1 = _read_limited(out)
            stderr, t2 = _read_limited(err)
        return Result(
            stdout=stdout,
            stderr=stderr,
            returncode=rc,
            timed_out=timed_out,
            interrupted=interrupted,
            truncated=t1 or t2,
        )

    def _stop_group(self, pgid: int, proc: subprocess.Popen, first: int) -> None:
        """Send ``first`` to the group, then SIGTERM and SIGKILL if needed."""
        signals = [first]
        if first != signal.SIGTERM:
            signals.append(signal.SIGTERM)
        signals.append(signal.SIGKILL)
        for sig in signals:
            _killpg(pgid, sig)
            _killpg(pgid, signal.SIGCONT)  # a stopped process cannot exit
            try:
                proc.wait(timeout=KILL_GRACE)
                return
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                continue

    # ----- background processes -------------------------------------------

    def prune(self) -> None:
        """Forget process groups that have ended."""
        self.pgids = {p for p in self.pgids if _group_alive(p)}

    def cleanup(self) -> None:
        """Stop every process this shell started (background jobs too)."""
        self.prune()
        for pgid in list(self.pgids):
            _killpg(pgid, signal.SIGTERM)
        deadline = time.monotonic() + KILL_GRACE
        while time.monotonic() < deadline and any(_group_alive(p) for p in self.pgids):
            time.sleep(0.05)
        for pgid in list(self.pgids):
            if _group_alive(pgid):
                _killpg(pgid, signal.SIGKILL)
        self.pgids.clear()


def _isatty(stream) -> bool:
    try:
        return stream.isatty()
    except (AttributeError, ValueError):
        return False


def _killpg(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _group_alive(pgid: int) -> bool:
    # Reap our own finished children first, or they count as "alive" zombies.
    try:
        while True:
            pid, _ = os.waitpid(-pgid, os.WNOHANG)
            if pid == 0:
                break
    except ChildProcessError:
        pass
    except OSError:
        pass
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False

