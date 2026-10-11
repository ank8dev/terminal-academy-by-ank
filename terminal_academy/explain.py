"""Offline notes for the in-app command ``explain <command>``.

This is the old desktop app's "explain this command" idea, but with short,
pre-written notes: no AI, no network, works everywhere.
"""

from __future__ import annotations

import re
from typing import List, Optional

NOTES = {
    "pwd": "pwd means 'print working directory'. It shows the folder you are "
           "standing in right now, as a full path from the top (/).",
    "ls": "ls lists what is in a folder. Try ls -l for details (size, date, "
          "permissions) and ls -a to also see hidden files (names starting with a dot).",
    "cd": "cd means 'change directory': it moves you into another folder. "
          "cd .. goes up one level, cd ~ (or just cd) goes to your home folder.",
    "echo": "echo prints the text you give it. It is great for quick messages, "
            "and together with > it can write text into a file: echo hi > note.txt",
    "cat": "cat prints the whole content of a file to the screen. Its name comes "
           "from 'concatenate', because it can also join files: cat a.txt b.txt",
    "less": "less shows a long file one screen at a time. Use the arrow keys or "
            "Space to scroll, /word to search, and q to quit.",
    "head": "head shows the first lines of a file (10 by default). head -n 3 "
            "file.txt shows only the first 3.",
    "tail": "tail shows the last lines of a file (10 by default). tail -n 5 "
            "file.txt shows the last 5. Handy for log files, where new lines go at the end.",
    "wc": "wc means 'word count'. It counts lines, words and bytes. wc -l counts "
          "only lines, which is the most useful one.",
    "mkdir": "mkdir means 'make directory': it creates a new folder. mkdir -p "
             "a/b/c creates all the missing folders on the way.",
    "touch": "touch creates an empty file. If the file already exists, it only "
             "updates the file's time stamp and does not change the content.",
    "cp": "cp copies a file: cp FROM TO. The original stays where it is. To copy "
          "a whole folder, use cp -r.",
    "mv": "mv moves OR renames. mv a.txt b.txt renames a file; mv a.txt folder/ "
          "moves it into a folder. Careful: it replaces a file with the same name.",
    "rm": "rm removes files. There is NO trash can: the file is gone for good. "
          "rm -r removes a folder and everything in it, so always check twice.",
    "rmdir": "rmdir removes an EMPTY folder. If the folder still has files in "
             "it, rmdir refuses, which makes it a safe choice.",
    "grep": "grep searches for text inside files and prints the matching lines. "
            "-i ignores upper/lower case, -n shows line numbers, -r searches "
            "every file in a folder.",
    "find": "find looks for files by name (or size, or type) in a folder and all "
            "folders inside it. Example: find . -name '*.txt'",
    "sort": "sort puts lines in order (A to Z). sort -n sorts numbers, sort -r "
            "reverses the order.",
    "uniq": "uniq removes repeated lines that are next to each other. That is "
            "why you usually sort first: sort names.txt | uniq. uniq -c also counts them.",
    "chmod": "chmod changes who may read (r), write (w) or run (x) a file. "
             "chmod +x script.sh makes a script runnable; chmod 600 key makes "
             "a file private to you.",
    "ps": "ps lists running processes (programs). Each one has a number, the "
          "PID. ps aux shows every process on the computer.",
    "kill": "kill sends a signal to a process, usually to stop it: kill 1234 "
            "stops the process with PID 1234. kill -9 forces it, as a last resort.",
    "sleep": "sleep waits for a number of seconds and does nothing else. It is "
             "perfect for practicing with processes: sleep 60 &",
    "jobs": "jobs lists the background jobs of the current shell. In Terminal "
            "Academy every line is a new shell, so try it in one line: sleep 5 & jobs",
    "export": "export makes a variable visible to programs you start: export "
              "NAME=value. Without export, only the shell itself knows it.",
    "env": "env prints all environment variables: settings like HOME, PATH and "
           "USER that every program can read.",
    "which": "which tells you where a command's program file lives, for example "
             "which ls prints /bin/ls. It searches the folders listed in $PATH.",
    "curl": "curl downloads things from a web address and prints them. In this "
            "course you use it with your own little web server on 127.0.0.1, so "
            "no internet is needed.",
    "hostname": "hostname prints the name of your computer on the network.",
    "ssh": "ssh opens a secure connection to another computer, so you can type "
           "commands there. Terminal Academy never connects anywhere; you only "
           "practice the settings with ssh -G.",
    "ssh-keygen": "ssh-keygen makes a pair of SSH keys: a private key (keep it "
                  "secret, never share it!) and a public key ending in .pub "
                  "(that one you can give to servers).",
    "python3": "python3 runs the Python programming language. python3 script.py "
               "runs a script; python3 -m http.server starts a tiny web server.",
    "man": "man shows the manual page of a command, for example man ls. Scroll "
           "with the arrow keys and press q to quit.",
    "clear": "clear wipes the screen so you have a clean view. Your files are "
             "not touched. In many terminals Ctrl+L does the same.",
    "history": "history lists the commands you typed before. In a normal "
               "terminal, the up arrow brings back the previous command too.",
    "tar": "tar packs many files into one archive file (and unpacks them). "
           "tar -czf box.tar.gz folder packs; tar -xzf box.tar.gz unpacks.",
    "ping": "ping checks if another computer answers, and how fast. Always use "
            "-c to stop after a few tries: ping -c 2 127.0.0.1",
    "sh": "sh and bash are shells: the programs that read your commands and run "
          "them. sh script.sh runs a script with sh. Terminal Academy runs your "
          "commands with bash.",
    "|": "The pipe | sends the output of one command into the next one as its "
         "input. Example: ls | wc -l counts the files in a folder.",
    ">": "> sends a command's output into a file instead of the screen. Careful: "
         "> replaces the file's content. Use >> to add to the end instead.",
}

ALIASES = {
    "bash": "sh",
    "zsh": "sh",
    "python": "python3",
    "pipe": "|",
    ">>": ">",
    "redirect": ">",
    "more": "less",
    "dir": "ls",
}


def topics() -> List[str]:
    return sorted(NOTES)


def lookup(query: str) -> Optional[str]:
    """Return the note for a command (or the first word of a command line)."""
    query = query.strip()
    if not query:
        return None
    if query in NOTES:
        return NOTES[query]
    if query in ALIASES:
        return NOTES[ALIASES[query]]
    word = re.split(r"\s+", query)[0]
    word = word.rsplit("/", 1)[-1]
    word = ALIASES.get(word, word)
    return NOTES.get(word)
