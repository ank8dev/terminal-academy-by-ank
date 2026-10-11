# Terminal Academy: Lessons Plan

This document is the plan for the lessons in the **Terminal Academy CLI app**.
It has four parts:

1. Goals and principles
2. The lesson format (the spec a developer implements)
3. The lessons: a table, then each lesson in detail
4. Safety and cross-platform notes

The app is a small Python program (Python 3.9+, standard library only). It runs on
**macOS and Linux**. It teaches teenagers (13–18) and other beginners how to use
the terminal.

---

## 1. Goals and principles

**Goals**

- A beginner with zero terminal experience can finish all lessons in a few hours.
- Every lesson is **hands-on**: the student types real shell commands, and the app
  checks the result automatically.
- After the course, the student can move around, manage files, search, use pipes,
  write a tiny script, understand permissions, processes, basic networking, and SSH keys.

**Principles**

- **Friendly and concrete.** Short sentences. Fun file names (dragons, games, music).
  No heavy jargon. Explain a word the first time we use it.
- **Safe.** Every lesson runs in its own sandbox folder. Dangerous commands are blocked.
  No root, no `sudo`, no real remote servers.
- **Small steps.** 3–6 steps per lesson, 5–10 minutes per lesson.
  Each step teaches one idea.
- **Learn by doing, then explain.** The student does the step first. After success,
  the app shows a short `explain` text with the concept.
- **Help is always there.** Hints come one by one. The student can `skip` or `reset`.
- **Works everywhere.** Only commands that work the same on macOS (BSD tools) and
  Linux (GNU tools). Works offline. Nothing to install.
- **Simple engine.** A small, fixed set of check types. Lessons are plain JSON files,
  so new lessons can be added without changing code.

---

## 2. The lesson format

### 2.1 Files and folders

```
<app>/lessons/
    01-first-steps.json
    02-moving-around.json
    ...
~/.terminal-academy/
    progress.json              # saved progress (see 2.8)
    sandbox/
        01-first-steps/        # sandbox root for this lesson
        02-moving-around/
        ...
```

- One JSON file per lesson. The file name is `<id>.json`.
- Lessons are shown in the menu sorted by `id` (the number prefix gives the order).
- Files are UTF-8. Text uses `\n` for new lines.

### 2.2 Top-level fields

| Field            | Type             | Required | Meaning |
|------------------|------------------|----------|---------|
| `format_version` | integer          | yes      | Always `1` for now. |
| `id`             | string           | yes      | Unique id, same as the file name without `.json`. Pattern: `^[0-9]{2}-[a-z0-9-]+$`, e.g. `"01-first-steps"`. |
| `title`          | string           | yes      | Short title shown in menus, e.g. `"First Steps"`. |
| `level`          | integer 1–5      | yes      | Difficulty. 1 = very easy, 5 = hardest. |
| `minutes`        | integer          | no       | Estimated time, e.g. `7`. |
| `summary`        | string           | yes      | One sentence for the lesson list. |
| `intro`          | string           | yes      | Text shown when the lesson starts (can have several lines). |
| `outro`          | string           | no       | Text shown when the lesson is finished. |
| `requires`       | list of strings  | no       | Programs the whole lesson needs, e.g. `["curl"]`. If one is missing, the menu shows a warning, but the lesson can still be opened. |
| `setup`          | list of objects  | yes      | Files and folders to create in the sandbox before the lesson starts (can be empty `[]`). |
| `steps`          | list of objects  | yes      | The steps (at least 1). |

### 2.3 `setup` entries

Each entry creates one file or one folder, in the order given.

| Field     | Type    | Meaning |
|-----------|---------|---------|
| `path`    | string  | Relative to the sandbox root. Must not start with `/` and must not contain `..`. Parent folders are created automatically. |
| `content` | string  | Text content of the file. Default `""` (empty file). Ignored when `dir` is true. |
| `dir`     | boolean | If `true`, create a folder instead of a file. Default `false`. |
| `mode`    | string  | Optional permission bits in octal, e.g. `"755"`, `"644"`, `"700"`. Applied with `chmod` after creating. If missing: files `644`, folders `755` (set explicitly, so the student's `umask` does not matter). |

Examples:

```json
{"path": "hello.txt", "content": "Welcome!\n"}
{"path": "music", "dir": true}
{"path": "bin/hello", "content": "#!/bin/sh\necho Hi\n", "mode": "755"}
```

### 2.4 `steps` entries

| Field         | Type            | Required | Meaning |
|---------------|-----------------|----------|---------|
| `instruction` | string          | yes      | What the student should do. |
| `hints`       | list of strings | yes      | 1 or more hints. The `hint` command shows the next one. The last hint usually shows the exact command. |
| `check`       | object          | yes      | How the engine knows the step is done (see 2.5). |
| `explain`     | string          | yes      | Short teaching text shown after success. |
| `solution`    | string          | no       | Exact command(s) that solve the step, one per line. **Not shown to students** during the step. Used by automated tests (see 2.10). May be shown after `skip`. |
| `requires`    | list of strings | no       | Programs this step needs, e.g. `["ping"]`. If one is missing (checked with `shutil.which`), the engine shows a friendly note and auto-skips the step. |
| `optional`    | boolean         | no       | If `true`, skipping this step does not count as "skipped" in progress. Default `false`. |

### 2.5 Check types (fixed set)

A check is a JSON object with a `type` and parameters at the same level:

```json
{"type": "file_exists", "path": "notes.txt"}
```

The engine supports **exactly these types**:

| Type              | Parameters                   | Passes when… |
|-------------------|------------------------------|--------------|
| `command_matches` | `pattern` (regex string)     | The command the student just typed matches the regex. Uses Python `re.search(pattern, command.strip())`. Use `^` to anchor at the start. |
| `output_contains` | `text` (string), optional `stream`: `"stdout"` (default), `"stderr"` or `"both"` | The output of the command just run contains `text` (exact, case-sensitive substring). `text` may contain `\n`. |
| `file_exists`     | `path`                       | `path` exists and is a regular file. |
| `dir_exists`      | `path`                       | `path` exists and is a folder. |
| `path_missing`    | `path`                       | Nothing exists at `path` (no file, no folder, no symlink). |
| `file_contains`   | `path`, `text`               | `path` is a regular file and its text contains `text` (exact substring; read as UTF-8 with `errors="replace"`). |
| `file_mode`       | `path`, `mode` (e.g. `"755"`) | `path` exists and `oct(stat.S_IMODE(st_mode) & 0o777)` equals `mode` (compare as 3-digit octal, e.g. `"600"`). Works for files and folders. |
| `cwd_is`          | `path`                       | The student's current folder equals `path`. `"."` means the sandbox root. Compare `os.path.realpath()` of both sides (important on macOS, where `/tmp` → `/private/tmp`). |
| `all`             | `checks` (list of checks)    | Every sub-check passes. Sub-checks can be any type, including `all`. |

**Rules for all checks**

- All `path` values are **relative to the sandbox root** of the lesson (not to the
  student's current folder). No leading `/`, no `..`.
- **When checks run:** after every shell command the engine actually runs
  (not after blocked commands, and not after in-app commands like `hint`).
  The engine checks only the **current step**.
- `command_matches` and `output_contains` look at the **last command only**.
  File checks look at the **current state of the sandbox**, so they pass no matter
  which command made the change.
- If the check passes: print "✓ Nice!" (or similar), print `explain`, go to the next step.
- If the check fails: say nothing special (just show the command output).
  After 3 failed attempts on the same step, print a gentle tip: "Stuck? Type `hint`."
- Regex note: in JSON files the backslash must be doubled. The regex `^ls\s` is
  written `"^ls\\s"` in JSON. All checks in this document are written as JSON.
- A lesson writer must make sure a step's check does **not** already pass right after
  setup or right after the previous step (the lesson test, 2.10, should verify this).

### 2.6 Example lesson (complete)

```json
{
  "format_version": 1,
  "id": "03-files-and-folders",
  "title": "Files and Folders",
  "level": 1,
  "minutes": 8,
  "summary": "Create, copy, move and delete files and folders.",
  "intro": "Your sandbox is a little messy.\nIn this lesson you will build folders, make files, copy them, rename them and clean up.\nEverything happens only inside your sandbox, so you can't break anything.",
  "outro": "Great job! You can now organize files like a pro.",
  "setup": [
    {"path": "old_name.txt", "content": "rename me\n"},
    {"path": "junk.txt", "content": "delete me\n"},
    {"path": "empty_box", "dir": true}
  ],
  "steps": [
    {
      "instruction": "Make a new folder called projects.",
      "hints": [
        "The command to make a directory is mkdir.",
        "Type: mkdir projects"
      ],
      "check": {"type": "dir_exists", "path": "projects"},
      "explain": "mkdir means 'make directory'. A directory is the same thing as a folder.",
      "solution": "mkdir projects"
    },
    {
      "instruction": "Make the folders projects/game/levels in ONE command.",
      "hints": [
        "mkdir has an option that creates the parent folders too: -p",
        "Type: mkdir -p projects/game/levels"
      ],
      "check": {"type": "dir_exists", "path": "projects/game/levels"},
      "explain": "mkdir -p creates every missing folder on the path. Without -p, mkdir fails if 'game' does not exist yet.",
      "solution": "mkdir -p projects/game/levels"
    },
    {
      "instruction": "Create an empty file projects/game/notes.txt",
      "hints": [
        "touch creates an empty file.",
        "Type: touch projects/game/notes.txt"
      ],
      "check": {"type": "file_exists", "path": "projects/game/notes.txt"},
      "explain": "touch creates an empty file, or updates the time of a file that already exists.",
      "solution": "touch projects/game/notes.txt"
    },
    {
      "instruction": "Copy projects/game/notes.txt to projects/game/notes_backup.txt",
      "hints": [
        "cp means copy: cp FROM TO",
        "Type: cp projects/game/notes.txt projects/game/notes_backup.txt"
      ],
      "check": {"type": "all", "checks": [
        {"type": "file_exists", "path": "projects/game/notes.txt"},
        {"type": "file_exists", "path": "projects/game/notes_backup.txt"}
      ]},
      "explain": "cp copies a file. The original stays. To copy a whole folder, use cp -r.",
      "solution": "cp projects/game/notes.txt projects/game/notes_backup.txt"
    },
    {
      "instruction": "Rename old_name.txt to new_name.txt",
      "hints": [
        "In the terminal, renaming is the same as moving: mv",
        "Type: mv old_name.txt new_name.txt"
      ],
      "check": {"type": "all", "checks": [
        {"type": "path_missing", "path": "old_name.txt"},
        {"type": "file_contains", "path": "new_name.txt", "text": "rename me"}
      ]},
      "explain": "mv moves OR renames. mv a.txt b.txt renames. mv a.txt folder/ moves it into the folder.",
      "solution": "mv old_name.txt new_name.txt"
    },
    {
      "instruction": "Clean up: delete junk.txt and the empty folder empty_box.",
      "hints": [
        "rm deletes a file. rmdir deletes an EMPTY folder.",
        "Type: rm junk.txt   and then:   rmdir empty_box"
      ],
      "check": {"type": "all", "checks": [
        {"type": "path_missing", "path": "junk.txt"},
        {"type": "path_missing", "path": "empty_box"}
      ]},
      "explain": "Careful: rm does NOT use a trash can. The file is gone forever. Always check twice before you press Enter.",
      "solution": "rm junk.txt\nrmdir empty_box"
    }
  ]
}
```

### 2.7 In-app commands

The student types these at the prompt. A line is an in-app command only when the
**whole line** is exactly one of these words (spaces around are ignored).
So `help` is an in-app command, but `help cd` goes to bash.

| Command   | What it does |
|-----------|--------------|
| `hint`    | Show the next hint for the current step. When all hints are shown, repeat the last one. |
| `skip`    | Skip the current step. Ask "Are you sure? (y/n)". Show the `solution` (if any), mark the step as skipped, go to the next step. Note: later steps may need the result of the skipped step; the app may run the `solution` automatically to keep the sandbox correct (recommended). |
| `reset`   | Ask for confirmation. Delete the sandbox, run `setup` again, reset the saved environment variables, kill background processes of this lesson, and restart the lesson at step 1. |
| `lessons` | Show the list of lessons with status (✓ done, ▶ in progress, · not started, ! missing tool). |
| `menu`    | Leave the current lesson (progress is saved) and go back to the main menu. |
| `help`    | Show the current instruction again and a short list of these in-app commands. |
| `quit`    | Save progress, stop background processes of the lesson, and exit the app. `Ctrl+D` does the same. |

`Ctrl+C` while a command is running stops that command (sends SIGINT to its process
group). `Ctrl+C` at an empty prompt does **not** quit; it prints "Type quit to exit."

### 2.8 Progress file

`~/.terminal-academy/progress.json`:

```json
{
  "version": 1,
  "lessons": {
    "01-first-steps": {"status": "done", "step": 5, "hints_used": 2, "skipped": [], "finished_at": "2026-10-11T15:20:00"},
    "02-moving-around": {"status": "in_progress", "step": 3, "hints_used": 0, "skipped": [1]}
  }
}
```

- `status`: `"not_started"`, `"in_progress"`, `"done"`.
- `step`: 0-based index of the current step (or the number of steps when done).
- Write the file after every finished step (write to a temp file, then `os.replace`).
- When a student opens an `in_progress` lesson, ask: "Continue where you stopped, or
  start again?" Continue = keep sandbox and step. Start again = same as `reset`.
- A missing or broken progress file is not an error: start fresh (keep a backup copy
  of a broken file as `progress.json.bak`).

### 2.9 How the engine runs commands (implementation notes)

This is the simple model the lessons in this plan are written for.

1. **Shell.** Use `bash` if found (`shutil.which("bash")`), else `sh`. Each student
   command runs in a **new** shell process: `bash -c '<wrapper>'`.
2. **Current folder.** The engine remembers the student's current folder (starts at
   the sandbox root). The command runs in that folder. After the command, the wrapper
   writes the new `pwd` to a state file, so `cd` "sticks".
   If the new folder is **outside** the sandbox, the engine moves the student back to
   the sandbox root and prints: "That folder is outside your sandbox, so I moved you back."
3. **Environment.** `HOME` is set to the sandbox root. So `cd`, `cd ~` and `~/.ssh`
   all stay inside the sandbox. After the command, the wrapper saves `export -p` to a
   state file, and the next command loads it first. So `export NAME=value` and changes
   to `PATH` stick. (Persisting plain, non-exported variables is a nice-to-have; the
   lessons always use `export`.) `reset` restores the original environment.
   A simple wrapper looks like:
   ```sh
   . "$TA_STATE/env.sh" 2>/dev/null
   cd "$TA_CWD" || exit 1
   <student command>
   __ta=$?
   pwd > "$TA_STATE/cwd"
   export -p > "$TA_STATE/env.sh"
   exit $__ta
   ```
   (Put the student command on its own line, so `#` comments in it cannot hide the rest.
   Remove `TA_*` variables from the saved environment.)
4. **Output.** stdout and stderr are written to two temp **files** (not pipes) and
   then printed to the screen. Files, because a background job (`sleep 300 &`) keeps a
   pipe open and the engine would wait forever. `stdin` is `/dev/null`, so commands
   like `cat` with no file do not hang.
5. **Interactive programs.** If the first word is one of `less`, `more`, `man`, `nano`,
   `vi`, `vim`, `top`, `htop`, `clear`, the command runs attached to the real terminal
   (no capture, no new process group). `output_contains` cannot be used for these steps;
   use `command_matches`.
6. **Process groups.** Captured commands start in their own process group
   (`preexec_fn=os.setpgrp`) — but in the same session, so they keep the terminal and
   `ps` still shows them. The engine remembers every group id. When the student leaves
   the lesson (`menu`, `quit`, `reset`, lesson done), it sends `SIGTERM` to all of them
   (ignore errors). This stops forgotten `sleep` and web servers.
7. **Timeout.** A foreground command is stopped after **30 seconds**
   (`SIGTERM`, then `SIGKILL` after 2 s, to the whole group) with the message
   "That took too long, so I stopped it. Tip: add & to run it in the background."
8. **One shell per command — what it means for students.** `jobs`, `fg` and `%1` only
   know jobs started **in the same line** (e.g. `sleep 5 & jobs`). Lesson 10 explains this.
9. **Prompt.** Show the path relative to the sandbox, e.g. `academy:~/school/math $ `.
   Use the `readline` module if available (history with the arrow keys; Tab completion
   for file names is a nice-to-have). On macOS `readline` may be `libedit`; that is OK.
10. **Blocked commands.** Before running, check the line against the blocklist (see 4.1).
    If it matches, do not run it, and print a friendly reason.

### 2.10 Testing lessons (for the developer)

Write one automatic test that, for every lesson file:

- validates the JSON (required fields, types, `id` = file name, level 1–5, regexes compile,
  setup paths are relative and have no `..`, check types are known);
- creates a temp sandbox, runs `setup`, then for each step:
  checks that the step's check **fails** before its `solution`, runs the `solution`
  through the same engine, and checks that it **passes** after;
- skips steps whose `requires` tools are missing.

Run this test on both macOS and Linux (e.g. in CI with `ubuntu-latest` and `macos-latest`).

---

## 3. The lessons

### 3.1 Overview

| #  | id                       | Title                    | Level | Min | Main commands |
|----|--------------------------|--------------------------|-------|-----|---------------|
| 1  | `01-first-steps`         | First Steps              | 1 | 5  | `pwd`, `ls`, `echo`, `clear`, `man`, `--help` |
| 2  | `02-moving-around`       | Moving Around            | 1 | 6  | `cd`, `..`, `~`, `ls -a`, paths |
| 3  | `03-files-and-folders`   | Files and Folders        | 1 | 8  | `mkdir`, `touch`, `cp`, `mv`, `rm`, `rmdir` |
| 4  | `04-reading-files`       | Reading Files            | 2 | 6  | `cat`, `head`, `tail`, `wc`, `less` |
| 5  | `05-searching`           | Finding Things           | 2 | 8  | `grep`, `grep -i/-n/-r`, `find` |
| 6  | `06-pipes-and-redirection` | Pipes and Redirection  | 2 | 8  | `>`, `>>`, `\|`, `sort`, `uniq`, `wc -l` |
| 7  | `07-permissions`         | Who Can Do What?         | 3 | 7  | `ls -l`, `chmod`, `./script` |
| 8  | `08-first-script`        | Your First Script        | 3 | 10 | `#!/bin/sh`, `$1`, `for`, `$(...)` |
| 9  | `09-variables-and-path`  | Variables and PATH       | 3 | 8  | `$HOME`, `env`, `export`, `$PATH`, `which` |
| 10 | `10-processes`           | Processes                | 4 | 8  | `ps`, `sleep`, `&`, `$!`, `kill`, `jobs` |
| 11 | `11-network-basics`      | Network Basics           | 4 | 7  | `hostname`, `/etc/hosts`, `127.0.0.1`, `ping`, `curl`, ports |
| 12 | `12-local-web-server`    | Your Own Web Server      | 4 | 8  | `python3 -m http.server`, `curl`, HTTP codes |
| 13 | `13-ssh-keys`            | SSH Keys                 | 5 | 8  | `ssh-keygen`, `~/.ssh`, `authorized_keys` |
| 14 | `14-ssh-config`          | SSH Config               | 5 | 7  | `~/.ssh/config`, `ssh -G` |
| 15 | `15-mini-project`        | Mini Project: Fan Site   | 5 | 10 | everything together |

### 3.2 How to read the lesson details

For every step you see:

- **Do:** the instruction (short version).
- **Check:** the exact check JSON.
- **Solution:** a command that solves it.
- **Hints:** 1–2 hints (the last hint can show the command).

The `explain` text is described in a few words; the writer makes it friendly.

---

### Lesson 1 — `01-first-steps` — First Steps (level 1, ~5 min)

**Learning goals:** what a terminal and a command are; `pwd`; `ls`; `echo`; `clear`;
how to get help with `man` and `--help`.

**Intro idea:** "The terminal is a way to talk to your computer with text. You type a
command, press Enter, and the computer answers."

**Setup:**
```json
[
  {"path": "hello.txt", "content": "Welcome to Terminal Academy!\n"},
  {"path": "music", "dir": true},
  {"path": "photos", "dir": true}
]
```

**Step 1 — Where am I?**
- Do: Type `pwd` to see which folder you are in.
- Check: `{"type": "command_matches", "pattern": "^pwd\\s*$"}`
- Solution: `pwd`
- Hints: "pwd means 'print working directory'." / "Type: pwd"
- Explain: the working directory is the folder you are "standing in". The long path is
  your sandbox.

**Step 2 — What is here?**
- Do: List the files in this folder.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^ls\\b"}, {"type": "output_contains", "text": "hello.txt"}]}`
- Solution: `ls`
- Hints: "The command is two letters, short for 'list'." / "Type: ls"
- Explain: `ls` shows files and folders. On many terminals folders have a different color.

**Step 3 — Make the computer talk**
- Do: Print the text `Hello, terminal!`
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^echo\\b"}, {"type": "output_contains", "text": "Hello, terminal!"}]}`
- Solution: `echo "Hello, terminal!"`
- Hints: "echo repeats what you give it." / `Type: echo "Hello, terminal!"`
- Explain: `echo` prints text. Quotes keep the words together as one piece of text.

**Step 4 — Clean screen**
- Do: Clear the screen.
- Check: `{"type": "command_matches", "pattern": "^clear\\s*$"}`
- Solution: `clear`
- Hints: "The command is the English word for 'make empty'." / "Type: clear (or press Ctrl+L in a real terminal)"
- Explain: `clear` only cleans the screen; your files are not touched.

**Step 5 — Ask for help** (`optional: true`)
- Do: Open the manual for `ls` (press `q` to quit it). If `man` is missing, try `curl --help` or `python3 --help`.
- Check: `{"type": "command_matches", "pattern": "^(man\\s+\\S+|\\S+\\s+--help)"}`
- Solution: `man ls`
- Hints: "man means 'manual'. Inside it, use the arrow keys and press q to quit." / "Type: man ls"
- Explain: almost every command has a manual page. Many commands also have `--help`,
  but not all (on macOS, `ls --help` does not work — `man ls` always does).

---

### Lesson 2 — `02-moving-around` — Moving Around (level 1, ~6 min)

**Learning goals:** `cd` into folders, `cd ..`, `cd ~`/`cd`, hidden files with `ls -a`,
relative vs. absolute paths.

**Setup:**
```json
[
  {"path": "school/math/homework.txt", "content": "2 + 2 = 4\n"},
  {"path": "school/art/drawing.txt", "content": "A dragon, drawn with letters.\n"},
  {"path": "games", "dir": true},
  {"path": ".secret_note.txt", "content": "You found the hidden file!\n"}
]
```

**Step 1 — Go into a folder**
- Do: Go into the folder `school`.
- Check: `{"type": "cwd_is", "path": "school"}`
- Solution: `cd school`
- Hints: "cd means 'change directory'." / "Type: cd school"
- Explain: the prompt now shows `school`. You moved, like opening a folder.

**Step 2 — Deeper**
- Do: Now go into `math`.
- Check: `{"type": "cwd_is", "path": "school/math"}`
- Solution: `cd math`
- Hints: "You are already in school, so just say the next folder." / "Type: cd math"
- Explain: a path like `math` is **relative**: it starts from where you are now.

**Step 3 — Go back up**
- Do: Go back up one folder.
- Check: `{"type": "cwd_is", "path": "school"}`
- Solution: `cd ..`
- Hints: "Two dots `..` mean 'the folder above me'." / "Type: cd .."
- Explain: `.` is the current folder, `..` is the parent folder.

**Step 4 — Go home**
- Do: Jump back to your home folder.
- Check: `{"type": "cwd_is", "path": "."}`
- Solution: `cd ~`
- Hints: "The symbol ~ means 'home'. Also, cd with nothing after it goes home." / "Type: cd ~"
- Explain: in Terminal Academy, home (`~`) is your sandbox. In a real terminal, `~` is
  your own user folder, like `/Users/ank` (macOS) or `/home/ank` (Linux).

**Step 5 — Hidden files**
- Do: Show ALL files, also the hidden ones.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^ls\\s+(.*\\s)?-[a-zA-Z]*a"}, {"type": "output_contains", "text": ".secret_note.txt"}]}`
- Solution: `ls -a`
- Hints: "ls has an option -a for 'all'." / "Type: ls -a"
- Explain: files whose name starts with a dot are hidden. Settings files often are.

**Step 6 — Two levels in one jump**
- Do: Go into `school/art` with one command.
- Check: `{"type": "cwd_is", "path": "school/art"}`
- Solution: `cd school/art`
- Hints: "Join folder names with a slash /." / "Type: cd school/art"
- Explain: a path that starts with `/` is **absolute** (starts at the very top of the
  computer). A path without `/` at the start is relative. Tip for real terminals:
  press Tab to complete names.

---

### Lesson 3 — `03-files-and-folders` — Files and Folders (level 1, ~8 min)

**Learning goals:** `mkdir`, `mkdir -p`, `touch`, `cp`, `mv` (move and rename),
`rm`, `rmdir`; "rm has no trash can".

**Setup and steps:** see the complete example in section 2.6. Summary of steps and checks:

| Step | Do | Check |
|------|----|-------|
| 1 | `mkdir projects` | `{"type": "dir_exists", "path": "projects"}` |
| 2 | `mkdir -p projects/game/levels` | `{"type": "dir_exists", "path": "projects/game/levels"}` |
| 3 | `touch projects/game/notes.txt` | `{"type": "file_exists", "path": "projects/game/notes.txt"}` |
| 4 | `cp` notes to notes_backup | `all` of two `file_exists` |
| 5 | `mv old_name.txt new_name.txt` | `all`: `path_missing` old + `file_contains` new "rename me" |
| 6 | `rm junk.txt`, `rmdir empty_box` | `all` of two `path_missing` |

---

### Lesson 4 — `04-reading-files` — Reading Files (level 2, ~6 min)

**Learning goals:** print a whole file with `cat`; the start and end with `head` and
`tail`; count lines with `wc -l`; scroll long files with `less`.

**Setup:**
```json
[
  {"path": "poem.txt", "content": "The cursor blinks, it waits for me,\nI type a word, and then I see:\nthe computer listens, line by line,\nand every answer comes back fine.\n"},
  {"path": "numbers.txt", "content": "line 1\nline 2\nline 3\n...\nline 20\n"}
]
```
(The writer fills `numbers.txt` with 20 lines, `line 1` to `line 20`.)

**Step 1 — Read a file**
- Do: Show the whole poem.
- Check: `{"type": "output_contains", "text": "The cursor blinks"}`
- Solution: `cat poem.txt`
- Hints: "cat prints a file on the screen." / "Type: cat poem.txt"
- Explain: `cat` is great for short files. For long files it scrolls away too fast.

**Step 2 — Only the beginning**
- Do: Show only the first 3 lines of `numbers.txt`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^head\\b"}, {"type": "output_contains", "text": "line 3"}]}`
- Solution: `head -n 3 numbers.txt`
- Hints: "head shows the head (top) of a file. -n says how many lines." / "Type: head -n 3 numbers.txt"
- Explain: without `-n`, `head` shows 10 lines.

**Step 3 — Only the end**
- Do: Show only the last 2 lines.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^tail\\b"}, {"type": "output_contains", "text": "line 20"}]}`
- Solution: `tail -n 2 numbers.txt`
- Hints: "The opposite of head is tail." / "Type: tail -n 2 numbers.txt"
- Explain: `tail` is perfect for log files, where the newest lines are at the end.

**Step 4 — Count**
- Do: Count the lines in `numbers.txt`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^wc\\s+-l"}, {"type": "output_contains", "text": "20"}]}`
- Solution: `wc -l numbers.txt`
- Hints: "wc means 'word count'. -l counts lines." / "Type: wc -l numbers.txt"
- Explain: `wc` alone shows lines, words and characters.

**Step 5 — Scroll**
- Do: Open `poem.txt` in `less`. Scroll with arrows, quit with `q`.
- Check: `{"type": "command_matches", "pattern": "^less\\s+\\S+"}`
- Solution: `less poem.txt`
- Hints: "less is a viewer. Space = next page, q = quit." / "Type: less poem.txt"
- Explain: in `less`, type `/word` to search. `man` uses the same viewer.

---

### Lesson 5 — `05-searching` — Finding Things (level 2, ~8 min)

**Learning goals:** search inside files with `grep` (`-i`, `-n`, `-r`); find files by
name with `find`; quote patterns with `*`.

**Setup:**
```json
[
  {"path": "game_log.txt", "content": "INFO: game started\nINFO: player joined\nWARN: low health\nERROR: dragon not found\nINFO: level 2\nerror: low battery\nERROR: save failed\nINFO: game over\n"},
  {"path": "project/README.md", "content": "My game project\n"},
  {"path": "project/src/main.py", "content": "print('hello')\n# TODO: add sound\n"},
  {"path": "project/src/utils/helpers.py", "content": "def helper():\n    pass  # TODO: write this\n"},
  {"path": "project/notes/ideas.txt", "content": "A game with dragons.\n"},
  {"path": "deep/a/b/c/treasure.txt", "content": "You found the treasure!\n"}
]
```

**Step 1 — Find a word in a file**
- Do: Show only the lines with `ERROR` in `game_log.txt`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^grep\\b"}, {"type": "output_contains", "text": "ERROR: dragon not found"}]}`
- Solution: `grep ERROR game_log.txt`
- Hints: "grep WORD FILE shows the lines that contain WORD." / "Type: grep ERROR game_log.txt"
- Explain: `grep` is case-sensitive: `ERROR` and `error` are different.

**Step 2 — Ignore big and small letters**
- Do: Find `error` in any case (ERROR, error, …).
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^grep\\s+(.*\\s)?-[a-zA-Z]*i"}, {"type": "output_contains", "text": "error: low battery"}]}`
- Solution: `grep -i error game_log.txt`
- Hints: "The option -i means 'ignore case'." / "Type: grep -i error game_log.txt"
- Explain: options can be combined: `-in` is the same as `-i -n`.

**Step 3 — Line numbers**
- Do: Show matching lines **with line numbers**.
- Check: `{"type": "output_contains", "text": "4:ERROR: dragon not found"}`
- Solution: `grep -n ERROR game_log.txt`
- Hints: "-n adds the line number in front." / "Type: grep -n ERROR game_log.txt"
- Explain: line numbers help you find the line later in an editor.

**Step 4 — Search a whole folder**
- Do: Find every `TODO` inside the `project` folder and all its subfolders.
- Check: `{"type": "all", "checks": [{"type": "output_contains", "text": "project/src/main.py"}, {"type": "output_contains", "text": "helpers.py"}]}`
- Solution: `grep -r TODO project`
- Hints: "-r means 'recursive': look in all folders inside." / "Type: grep -r TODO project"
- Explain: programmers use this every day to find notes in code.

**Step 5 — Find a file by name**
- Do: Somewhere here is `treasure.txt`. Find it.
- Check: `{"type": "output_contains", "text": "deep/a/b/c/treasure.txt"}`
- Solution: `find . -name treasure.txt`
- Hints: "find WHERE -name NAME. The dot . means 'here'." / "Type: find . -name treasure.txt"
- Explain: `grep` looks **inside** files, `find` looks at file **names** (and types, sizes…).

**Step 6 — Find with a pattern**
- Do: Find all Python files (`*.py`).
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^find\\b"}, {"type": "output_contains", "text": "helpers.py"}, {"type": "output_contains", "text": "main.py"}]}`
- Solution: `find . -name "*.py"`
- Hints: "* means 'anything'. Put the pattern in quotes." / `Type: find . -name "*.py"`
- Explain: without quotes, the shell may replace `*.py` before `find` sees it. Quotes
  protect it. Always write the folder (`.`) — on macOS, `find` needs it.

---

### Lesson 6 — `06-pipes-and-redirection` — Pipes and Redirection (level 2, ~8 min)

**Learning goals:** save output to a file with `>`; add to a file with `>>`;
connect commands with `|`; `sort`, `uniq`, `wc -l`.

**Setup:**
```json
[
  {"path": "names.txt", "content": "Zoe\nBen\nAlice\nMax\nBen\nCarla\nAlice\nMax\nLeo\n"}
]
```

**Step 1 — Save output to a file**
- Do: Save the output of `ls` into a file `files.txt`.
- Check: `{"type": "file_contains", "path": "files.txt", "text": "names.txt"}`
- Solution: `ls > files.txt`
- Hints: "> sends the output into a file instead of the screen." / "Type: ls > files.txt"
- Explain: `>` creates the file, or **replaces** it if it already exists.

**Step 2 — Write a diary**
- Do: Write `Day 1: I learned pipes` into `diary.txt`.
- Check: `{"type": "file_contains", "path": "diary.txt", "text": "Day 1"}`
- Solution: `echo "Day 1: I learned pipes" > diary.txt`
- Hints: "Use echo and >." / `Type: echo "Day 1: I learned pipes" > diary.txt`
- Explain: `echo` + `>` is the fastest way to make a small text file.

**Step 3 — Add, don't replace**
- Do: Add a second line `Day 2: ...` to `diary.txt` without losing Day 1.
- Check: `{"type": "all", "checks": [{"type": "file_contains", "path": "diary.txt", "text": "Day 1"}, {"type": "file_contains", "path": "diary.txt", "text": "Day 2"}]}`
- Solution: `echo "Day 2: I learned >>" >> diary.txt`
- Hints: "Two arrows >> mean 'append' (add at the end)." / "If you lost Day 1, just write it again with >, then add Day 2 with >>."
- Explain: `>` = replace, `>>` = add. Mixing them up is a classic mistake.

**Step 4 — Your first pipe**
- Do: Sort the names, then remove repeated names, with ONE line.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "\\|\\s*uniq"}, {"type": "output_contains", "text": "Alice\nBen\nCarla"}]}`
- Solution: `sort names.txt | uniq`
- Hints: "| (the pipe) sends the output of one command into the next one." / "Type: sort names.txt | uniq"
- Explain: `uniq` only removes repeats that are **next to each other**. That's why we `sort` first.

**Step 5 — Pipe + save**
- Do: Save the unique, sorted names into `unique_names.txt`.
- Check: `{"type": "file_contains", "path": "unique_names.txt", "text": "Carla\nLeo\nMax\nZoe"}`
- Solution: `sort names.txt | uniq > unique_names.txt`
- Hints: "Put > file at the very end of the pipe." / "Type: sort names.txt | uniq > unique_names.txt"
- Explain: pipes and redirection work together like LEGO bricks.

**Step 6 — Count with a pipe**
- Do: Count how many different names there are.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "\\|\\s*wc\\s+-l"}, {"type": "output_contains", "text": "6"}]}`
- Solution: `sort names.txt | uniq | wc -l`
- Hints: "Add one more brick: | wc -l" / "Type: sort names.txt | uniq | wc -l"
- Explain: error messages go to a different stream (stderr). `2>` saves errors to a
  file, e.g. `ls nothing 2> errors.txt`.

---

### Lesson 7 — `07-permissions` — Who Can Do What? (level 3, ~7 min)

**Learning goals:** read `ls -l` (`rwx` for owner, group, others); change
permissions with `chmod` numbers (600, 644, 755); make a script executable and run
it with `./`.

**Setup:**
```json
[
  {"path": "diary.txt", "content": "My secret thoughts.\n", "mode": "644"},
  {"path": "hello.sh", "content": "#!/bin/sh\necho \"Hello from a script!\"\n", "mode": "644"}
]
```

**Step 1 — Look at permissions**
- Do: Show the files in the long format.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^ls\\s+(.*\\s)?-[a-zA-Z]*l"}, {"type": "output_contains", "text": "rw-r--r--"}]}`
- Solution: `ls -l`
- Hints: "-l means 'long'." / "Type: ls -l"
- Explain: `-rw-r--r--` = file; owner can read+write; group can read; others can read.
  `r`=read, `w`=write, `x`=execute (run).

**Step 2 — Make the diary private**
- Do: Only you should read and write `diary.txt`. Set it to 600.
- Check: `{"type": "file_mode", "path": "diary.txt", "mode": "600"}`
- Solution: `chmod 600 diary.txt`
- Hints: "Numbers: r=4, w=2, x=1. 6 = 4+2 = read+write. 0 = nothing." / "Type: chmod 600 diary.txt"
- Explain: three digits = owner, group, others. 600 = `rw-------`.

**Step 3 — Try to run the script**
- Do: Try to run `hello.sh` with `./hello.sh`. It will fail. That's the point!
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^\\./hello\\.sh\\s*$"}, {"type": "output_contains", "text": "Permission denied", "stream": "stderr"}]}`
- Solution: `./hello.sh`
- Hints: "./ means 'the file in this folder'." / "Type: ./hello.sh"
- Explain: the file has no `x` (execute) permission, so the computer refuses to run it.

**Step 4 — Make it executable**
- Do: Give `hello.sh` the mode 755.
- Check: `{"type": "file_mode", "path": "hello.sh", "mode": "755"}`
- Solution: `chmod 755 hello.sh`
- Hints: "7 = 4+2+1 = read+write+execute. 5 = 4+1 = read+execute." / "Type: chmod 755 hello.sh"
- Explain: 755 = `rwxr-xr-x`, the normal mode for scripts and programs. You may also
  see `chmod +x file`.

**Step 5 — Run it**
- Do: Run `./hello.sh` again.
- Check: `{"type": "output_contains", "text": "Hello from a script!"}`
- Solution: `./hello.sh`
- Hints: "Same command as before." / "Type: ./hello.sh"
- Explain: you just ran your first program from a file! Never use `chmod 777` — it lets
  everyone change your file.

---

### Lesson 8 — `08-first-script` — Your First Script (level 3, ~10 min)

**Learning goals:** write a script line by line with `echo` and `>>`; the shebang
`#!/bin/sh`; arguments (`$1`); a `for` loop; command substitution `$(...)`;
`sh script.sh` vs `./script.sh`.

**Setup:**
```json
[
  {"path": "notes.txt", "content": "buy milk\n"},
  {"path": "todo.txt", "content": "learn bash\n"},
  {"path": "cat.jpg", "content": ""},
  {"path": "dog.jpg", "content": ""}
]
```

**Step 1 — The first line**
- Do: Create `greet.sh` whose first line is `#!/bin/sh`.
- Check: `{"type": "file_contains", "path": "greet.sh", "text": "#!/bin/sh"}`
- Solution: `echo '#!/bin/sh' > greet.sh`
- Hints: "Use single quotes ' ' so the shell does not change the text." / "Type: echo '#!/bin/sh' > greet.sh"
- Explain: this line is the **shebang**. It tells the computer which program runs the script.

**Step 2 — Say hello to someone**
- Do: Add the line `echo "Hello, $1!"` to `greet.sh`.
- Check: `{"type": "file_contains", "path": "greet.sh", "text": "Hello, $1"}`
- Solution: `echo 'echo "Hello, $1!"' >> greet.sh`
- Hints: "Use >> to add a line. Outside single quotes, inside double quotes." / `Type: echo 'echo "Hello, $1!"' >> greet.sh`
- Explain: `$1` is the first word you give the script. Check your file with `cat greet.sh`.

**Step 3 — Make it executable**
- Do: Make `greet.sh` executable (755).
- Check: `{"type": "file_mode", "path": "greet.sh", "mode": "755"}`
- Solution: `chmod 755 greet.sh`
- Hints: "You did this in the last lesson." / "Type: chmod 755 greet.sh"
- Explain: now it can be run with `./greet.sh`.

**Step 4 — Run it with your name**
- Do: Run the script and give it your name.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^\\./greet\\.sh\\s+\\S+"}, {"type": "output_contains", "text": "Hello, "}]}`
- Solution: `./greet.sh Ank`
- Hints: "Write your name after the script name." / "Type: ./greet.sh Ank"
- Explain: `Ank` became `$1`. `$2` would be the second word, and so on.

**Step 5 — A loop**
- Do: Create `list.sh` that prints every `.txt` file, then run it with `sh list.sh`.
- Check: `{"type": "output_contains", "text": "Text file: notes.txt"}`
- Solution: `echo 'for f in *.txt; do echo "Text file: $f"; done' > list.sh` then `sh list.sh`
- Hints: "A loop: for f in *.txt; do ...; done" / `Type: echo 'for f in *.txt; do echo "Text file: $f"; done' > list.sh   and then: sh list.sh`
- Explain: `for` repeats a command for each item. `sh file` runs a script even
  without `x` permission.

**Step 6 — Add today's day**
- Do: Add a line to `greet.sh` that prints `Today is <weekday>`, then run `./greet.sh` again.
- Check: `{"type": "output_contains", "text": "Today is "}`
- Solution: `echo 'echo "Today is $(date +%A)"' >> greet.sh` then `./greet.sh Ank`
- Hints: "$(command) puts the output of a command inside text. date +%A prints the weekday." / `Type: echo 'echo "Today is $(date +%A)"' >> greet.sh   and then: ./greet.sh Ank`
- Explain: `$(...)` is called command substitution. Scripts are just commands saved in a file.

---

### Lesson 9 — `09-variables-and-path` — Variables and PATH (level 3, ~8 min)

**Learning goals:** what environment variables are; `$HOME`, `$USER`; list them with
`env`; create one with `export`; what `PATH` is; `which`; add your own folder to `PATH`.

**Setup:**
```json
[
  {"path": "bin/hello", "content": "#!/bin/sh\necho \"Hi! You just ran your own command.\"\n", "mode": "755"}
]
```

**Step 1 — Your home**
- Do: Print the value of the variable `HOME`.
- Check: `{"type": "command_matches", "pattern": "^echo\\s+\"?\\$\\{?HOME"}`
- Solution: `echo $HOME`
- Hints: "Put $ in front of a variable name to get its value." / "Type: echo $HOME"
- Explain: variables are named boxes with text inside. Here `HOME` is your sandbox.

**Step 2 — All variables**
- Do: Show all environment variables.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^(env|printenv)\\b"}, {"type": "output_contains", "text": "PATH="}]}`
- Solution: `env`
- Hints: "The command is short for 'environment'." / "Type: env"
- Explain: every program you start gets a copy of these variables.

**Step 3 — Make your own**
- Do: Create a variable `PET` with the value `dragon`, then print `My pet is a dragon` using it.
- Check: `{"type": "output_contains", "text": "My pet is a dragon"}`
- Solution: `export PET=dragon` then `echo "My pet is a $PET"`
- Hints: "No spaces around = !  export PET=dragon" / `Then: echo "My pet is a $PET"`
- Explain: `export` makes the variable visible to programs you start. In Terminal
  Academy, always use `export` so the app remembers it.

**Step 4 — The PATH**
- Do: Print the `PATH` variable.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "PATH"}, {"type": "output_contains", "text": "/bin"}]}`
- Solution: `echo $PATH`
- Hints: "Same as HOME, but with PATH." / "Type: echo $PATH"
- Explain: `PATH` is a list of folders, split by `:`. When you type `ls`, the shell looks
  for a program called `ls` in these folders.

**Step 5 — Where is ls?**
- Do: Find out where the program `ls` lives.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^(which|type|command\\s+-v)\\s+ls\\s*$"}, {"type": "output_contains", "text": "/ls"}]}`
- Solution: `which ls`
- Hints: "Ask the computer: which ls?" / "Type: which ls"
- Explain: commands are just program files in folders like `/bin` or `/usr/bin`.

**Step 6 — Your own command**
- Do: Type `hello` (it fails). Then add `$HOME/bin` to the front of `PATH`, and type `hello` again.
- Check: `{"type": "output_contains", "text": "Hi! You just ran your own command."}`
- Solution: `export PATH="$HOME/bin:$PATH"` then `hello`
- Hints: "New PATH = your folder + : + old PATH." / `Type: export PATH="$HOME/bin:$PATH"   and then: hello`
- Explain: this is how tools get "installed" for your user. If you break `PATH`
  by mistake, type `reset`.

---

### Lesson 10 — `10-processes` — Processes (level 4, ~8 min)

**Learning goals:** a process is a running program; `ps`; foreground vs. background
(`&`); the process ID (PID) and `$!`; stop a process with `kill`; `jobs`.

**Intro note:** "In Terminal Academy, every command line runs in a fresh shell. So
`jobs` only knows jobs from the same line. In your real terminal, it remembers more."

**Setup:**
```json
[
  {"path": "slow.sh", "content": "#!/bin/sh\necho start\nsleep 3\necho done\n", "mode": "755"}
]
```

**Step 1 — See processes**
- Do: Show your running processes.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^ps\\b"}, {"type": "output_contains", "text": "PID"}]}`
- Solution: `ps`
- Hints: "ps = 'process status'." / "Type: ps"
- Explain: every running program has a number, the **PID** (process ID).

**Step 2 — Foreground**
- Do: Run `./slow.sh` and wait for it.
- Check: `{"type": "output_contains", "text": "done"}`
- Solution: `./slow.sh`
- Hints: "It takes 3 seconds. Be patient!" / "Type: ./slow.sh"
- Explain: a **foreground** command blocks the terminal until it ends. `Ctrl+C` stops it.

**Step 3 — Background**
- Do: Start `sleep 300` in the background and print its PID.
- Check: `{"type": "command_matches", "pattern": "^sleep\\s+\\d+\\s*&"}`
- Solution: `sleep 300 & echo $!`
- Hints: "Put & at the end to run in the background. $! is the PID of the last background job." / "Type: sleep 300 & echo $!"
- Explain: `sleep 300` waits 300 seconds doing nothing. With `&` you get your prompt back at once.

**Step 4 — Find it**
- Do: Find the `sleep` process in the list of all processes.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "grep\\s+.*sleep"}, {"type": "output_contains", "text": "sleep 300"}]}`
- Solution: `ps aux | grep sleep`
- Hints: "ps aux shows ALL processes. Use a pipe and grep to filter." / "Type: ps aux | grep sleep"
- Explain: the second column is the PID. You will also see the `grep` itself in the list.

**Step 5 — Stop it**
- Do: Stop the `sleep` process with `kill` and its PID.
- Check: `{"type": "command_matches", "pattern": "^(kill\\s+(-[A-Z0-9]+\\s+)?\\d+|pkill\\s+(-f\\s+)?sleep)"}`
- Solution: `pkill sleep` (or `kill 12345` with the real PID)
- Hints: "kill PID, for example: kill 12345 (use YOUR number from step 4)." / "Lost the number? Run ps aux | grep sleep again."
- Explain: `kill` sends a signal asking a process to stop. `kill -9 PID` forces it —
  use it only when a normal `kill` does not work.

**Step 6 — jobs**
- Do: In ONE line, start `sleep 5` in the background and then list jobs.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "&\\s*jobs"}, {"type": "output_contains", "text": "Running"}]}`
- Solution: `sleep 5 & jobs`
- Hints: "Join them: first the background command with &, then jobs." / "Type: sleep 5 & jobs"
- Explain: in a real terminal, `jobs` lists background jobs, `fg` brings one back to the
  foreground, and `kill %1` stops job number 1.

---

### Lesson 11 — `11-network-basics` — Network Basics (level 4, ~7 min)

**Learning goals:** your computer's name (`hostname`); `localhost` = `127.0.0.1` = this
computer; the `/etc/hosts` file; `ping` (optional); URLs and `curl`; what a port is.
Everything works **offline**.

**Setup:**
```json
[
  {"path": "page.html", "content": "<h1>Hello offline web</h1>\n"}
]
```

**Step 1 — My computer's name**
- Do: Print your computer's name.
- Check: `{"type": "command_matches", "pattern": "^hostname\\s*$"}`
- Solution: `hostname`
- Hints: "host = a computer on a network." / "Type: hostname"
- Explain: every computer on a network has a name and an address (an IP address).

**Step 2 — The hosts file**
- Do: Show the file `/etc/hosts` (you may read it, but not change it).
- Check: `{"type": "output_contains", "text": "localhost"}`
- Solution: `cat /etc/hosts`
- Hints: "This file is outside your sandbox, but reading is fine. Use cat." / "Type: cat /etc/hosts"
- Explain: this file maps names to addresses. `localhost` → `127.0.0.1` means "this
  computer itself".

**Step 3 — Ping yourself** (`optional: true`, `requires: ["ping"]`)
- Do: Send 2 pings to `127.0.0.1`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^ping\\s+.*-c\\s*\\d"}, {"type": "output_contains", "text": "127.0.0.1"}]}`
- Solution: `ping -c 2 127.0.0.1`
- Hints: "-c 2 means 'count 2', so it stops by itself." / "Type: ping -c 2 127.0.0.1"
- Explain: `ping` checks if a computer answers. Without `-c` it never stops (Ctrl+C).

**Step 4 — curl reads a URL** (`requires: ["curl"]`)
- Do: Use `curl` to read `page.html` with a `file://` URL.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^curl\\b"}, {"type": "output_contains", "text": "Hello offline web"}]}`
- Solution: `curl "file://$HOME/page.html"`
- Hints: "A URL has a scheme (http, https, file), then ://, then the place." / `Type: curl "file://$HOME/page.html"`
- Explain: `curl` downloads what a URL points to and prints it. With internet,
  `curl https://example.com` would get a web page.

**Step 5 — Ports** (`optional: true`)
- Do: Find which port numbers `ssh`, `http` and `https` use in `/etc/services`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^grep\\b.*/etc/services"}, {"type": "output_contains", "text": "ssh"}]}`
- Solution: `grep -E "^(ssh|http|https)[[:space:]]" /etc/services`
- Hints: "A port is like a door number on a computer. grep the file /etc/services." / `Type: grep -E "^(ssh|http|https)[[:space:]]" /etc/services`
- Explain: one computer runs many services; each listens on a port: ssh = 22,
  http = 80, https = 443. (If the file does not exist on your system, `skip`.)

---

### Lesson 12 — `12-local-web-server` — Your Own Web Server (level 4, ~8 min)

**Learning goals:** start a real web server on your own computer; talk to it with
`curl`; HTTP status codes (200, 404); stop a background server. Offline, safe
(bound to `127.0.0.1` only).

**requires:** `["curl"]` (python3 is always there, because the app runs on it).

**Setup:**
```json
[
  {"path": "site/index.html", "content": "<h1>My first server</h1>\n"},
  {"path": "site/hello.txt", "content": "Hello from your server!\n"}
]
```

**Step 1 — Go to the site folder**
- Check: `{"type": "cwd_is", "path": "site"}`
- Solution: `cd site`
- Hints: "You know this one!" / "Type: cd site"
- Explain: the server will share the files of the folder it starts in.

**Step 2 — Start the server**
- Do: Start a web server on port 8765, only for this computer, in the background.
- Check: `{"type": "command_matches", "pattern": "^python3\\s+-m\\s+http\\.server\\b.*&\\s*$"}`
- Solution: `python3 -m http.server 8765 --bind 127.0.0.1 &`
- Hints: "Do not forget & at the end, or the server blocks your terminal." / "Type: python3 -m http.server 8765 --bind 127.0.0.1 &"
- Explain: a **server** is a program that waits for requests on a port. `--bind 127.0.0.1`
  means only your computer can reach it. If you see "Address already in use",
  use another port, like 8766, also in the next steps.

**Step 3 — Ask your server**
- Do: Get `hello.txt` from your server.
- Check: `{"type": "output_contains", "text": "Hello from your server!"}`
- Solution: `curl http://127.0.0.1:8765/hello.txt`
- Hints: "URL = http:// + address + : + port + /file" / "Type: curl http://127.0.0.1:8765/hello.txt"
- Explain: you are the **client**, Python is the **server**. That's how the web works.
  `http://localhost:8765/` works too.

**Step 4 — Look at the headers**
- Do: Ask only for the headers of the main page.
- Check: `{"type": "output_contains", "text": "200"}`
- Solution: `curl -I http://127.0.0.1:8765/`
- Hints: "-I asks only for the 'head' of the answer." / "Type: curl -I http://127.0.0.1:8765/"
- Explain: `200 OK` means "all good". Headers also tell the type and size of the content.

**Step 5 — A missing page**
- Do: Ask for a page that does not exist, like `/nope.html`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^curl\\b.*nope"}, {"type": "output_contains", "text": "404"}]}`
- Solution: `curl http://127.0.0.1:8765/nope.html`
- Hints: "Same as before, different file name." / "Type: curl http://127.0.0.1:8765/nope.html"
- Explain: `404 Not Found` — you have seen this on websites. Now you know where it comes from.

**Step 6 — Stop the server**
- Do: Find the server process and stop it.
- Check: `{"type": "command_matches", "pattern": "^(kill\\s+(-[A-Z0-9]+\\s+)?\\d+|pkill\\s+-f\\s+['\"]?\\S*http)"}`
- Solution: `pkill -f http.server`
- Hints: "ps aux | grep http.server shows the PID. Then kill PID." / "Or type: pkill -f http.server"
- Explain: always stop servers you don't need. (The app also stops them when you leave the lesson.)

---

### Lesson 13 — `13-ssh-keys` — SSH Keys (level 5, ~8 min)

**Learning goals:** what SSH is (a safe remote terminal); key pairs: private key
(secret!) and public key (shareable); `ssh-keygen`; the `~/.ssh` folder and its
permissions; what `authorized_keys` does on a server. **No real server is used.**

**requires:** `["ssh-keygen"]`

**Setup:**
```json
[
  {"path": "fake_server/home/student/.ssh", "dir": true, "mode": "700"},
  {"path": "README.txt", "content": "fake_server/ pretends to be a server's disk.\n"}
]
```

**Step 1 — The .ssh folder**
- Do: Create the folder `.ssh` and make it private (700).
- Check: `{"type": "all", "checks": [{"type": "dir_exists", "path": ".ssh"}, {"type": "file_mode", "path": ".ssh", "mode": "700"}]}`
- Solution: `mkdir .ssh` then `chmod 700 .ssh`
- Hints: "Two commands: mkdir, then chmod." / "Type: mkdir .ssh   and then: chmod 700 .ssh"
- Explain: SSH refuses to use keys in folders that others can read. 700 = only you.

**Step 2 — Make a key pair**
- Do: Create an ed25519 key at `.ssh/id_academy` with no passphrase.
- Check: `{"type": "all", "checks": [{"type": "file_exists", "path": ".ssh/id_academy"}, {"type": "file_exists", "path": ".ssh/id_academy.pub"}]}`
- Solution: `ssh-keygen -t ed25519 -f .ssh/id_academy -N "" -C "student@academy"`
- Hints: "-t = type, -f = file, -N \"\" = empty passphrase, -C = comment." / `Type: ssh-keygen -t ed25519 -f .ssh/id_academy -N "" -C "student@academy"`
- Explain: you got TWO files: `id_academy` (private, never share it!) and
  `id_academy.pub` (public, safe to share). For real keys, use a passphrase.

**Step 3 — Check the permissions**
- Do: Look at the files in `.ssh` in long format.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^ls\\s+.*-[a-zA-Z]*l"}, {"type": "output_contains", "text": "rw-------"}]}`
- Solution: `ls -l .ssh`
- Hints: "ls -l + the folder name." / "Type: ls -l .ssh"
- Explain: `ssh-keygen` gave the private key mode 600 automatically. Good!

**Step 4 — The public key**
- Do: Show your public key.
- Check: `{"type": "output_contains", "text": "ssh-ed25519 "}`
- Solution: `cat .ssh/id_academy.pub`
- Hints: "It's the file that ends with .pub" / "Type: cat .ssh/id_academy.pub"
- Explain: this one line is what you paste into GitHub or give to a server admin.

**Step 5 — Fingerprint**
- Do: Show the fingerprint of your public key.
- Check: `{"type": "output_contains", "text": "ED25519"}`
- Solution: `ssh-keygen -l -f .ssh/id_academy.pub`
- Hints: "-l = list the fingerprint." / "Type: ssh-keygen -l -f .ssh/id_academy.pub"
- Explain: a fingerprint is a short "ID card" of a key. You use it to compare keys quickly.

**Step 6 — Put the key on the (fake) server**
- Do: Add your public key to `fake_server/home/student/.ssh/authorized_keys`.
- Check: `{"type": "file_contains", "path": "fake_server/home/student/.ssh/authorized_keys", "text": "ssh-ed25519 "}`
- Solution: `cat .ssh/id_academy.pub >> fake_server/home/student/.ssh/authorized_keys`
- Hints: "Use cat and >> (append)." / "Type: cat .ssh/id_academy.pub >> fake_server/home/student/.ssh/authorized_keys"
- Explain: on a real server, `authorized_keys` lists the keys that may log in. The command
  `ssh-copy-id user@server` does exactly this for you.

---

### Lesson 14 — `14-ssh-config` — SSH Config (level 5, ~7 min)

**Learning goals:** the `~/.ssh/config` file (nicknames for servers: `Host`, `HostName`,
`User`, `Port`, `IdentityFile`); its permissions; check a config **without
connecting** using `ssh -G`; what `known_hosts` is.

**Setup:**
```json
[
  {"path": ".ssh", "dir": true, "mode": "700"}
]
```

**Step 1 — A nickname**
- Do: Create `.ssh/config` with the line `Host myserver`.
- Check: `{"type": "file_contains", "path": ".ssh/config", "text": "Host myserver"}`
- Solution: `echo 'Host myserver' > .ssh/config`
- Hints: "Use echo and >." / "Type: echo 'Host myserver' > .ssh/config"
- Explain: `Host` starts a block. Later you can type `ssh myserver` instead of a long command.

**Step 2 — The real address**
- Do: Add `  HostName 192.168.1.50`.
- Check: `{"type": "file_contains", "path": ".ssh/config", "text": "HostName 192.168.1.50"}`
- Solution: `echo '  HostName 192.168.1.50' >> .ssh/config`
- Hints: "Use >> to add. The spaces at the start are just for reading." / "Type: echo '  HostName 192.168.1.50' >> .ssh/config"
- Explain: `HostName` is the real address (an IP or a domain name like `pi.local`).

**Step 3 — User and port**
- Do: Add `  User student` and `  Port 2222`.
- Check: `{"type": "all", "checks": [{"type": "file_contains", "path": ".ssh/config", "text": "User student"}, {"type": "file_contains", "path": ".ssh/config", "text": "Port 2222"}]}`
- Solution: `echo '  User student' >> .ssh/config` then `echo '  Port 2222' >> .ssh/config`
- Hints: "Two echo commands, both with >>." / "Type: echo '  User student' >> .ssh/config"
- Explain: the normal SSH port is 22. Some servers use another one.

**Step 4 — Which key**
- Do: Add `  IdentityFile ~/.ssh/id_academy`.
- Check: `{"type": "file_contains", "path": ".ssh/config", "text": "IdentityFile ~/.ssh/id_academy"}`
- Solution: `echo '  IdentityFile ~/.ssh/id_academy' >> .ssh/config`
- Hints: "Same as before, with >>." / "Type: echo '  IdentityFile ~/.ssh/id_academy' >> .ssh/config"
- Explain: this tells SSH which private key to use for this server.

**Step 5 — Protect it**
- Do: Make the config readable only by you (600).
- Check: `{"type": "file_mode", "path": ".ssh/config", "mode": "600"}`
- Solution: `chmod 600 .ssh/config`
- Hints: "Only read+write for you." / "Type: chmod 600 .ssh/config"
- Explain: SSH may refuse a config file that others can change.

**Step 6 — Test without connecting** (`optional: true`, `requires: ["ssh"]`)
- Do: Ask SSH what it would do for `myserver`, and filter for `hostname`.
- Check: `{"type": "output_contains", "text": "hostname 192.168.1.50"}`
- Solution: `ssh -F .ssh/config -G myserver | grep -i -E "^(hostname|user|port) "`
- Hints: "-F = which config file, -G = only print the settings, don't connect." / `Type: ssh -F .ssh/config -G myserver | grep -i -E "^(hostname|user|port) "`
- Explain: on the first real connection, SSH asks "Are you sure you want to continue
  connecting?" and saves the server's key in `~/.ssh/known_hosts`. That protects you
  from fake servers.

---

### Lesson 15 — `15-mini-project` — Mini Project: Fan Site (level 5, ~10 min)

**Learning goals:** use everything together: folders, wildcards, `mv`/`cp`, editing a
script, permissions, environment variables, running a script, a local server and `curl`.

**Intro idea:** "Your downloads folder is a mess. Turn it into a tiny website for your
favorite band, then serve it on your own computer."

**requires:** `["curl"]`

**Setup:**
```json
[
  {"path": "downloads/band.jpg", "content": ""},
  {"path": "downloads/logo.png", "content": ""},
  {"path": "downloads/setlist.txt", "content": "1. Intro\n2. Big Song\n3. Encore\n"},
  {"path": "downloads/tour.txt", "content": "Berlin, Paris, Tokyo\n"},
  {"path": "downloads/song.mp3", "content": ""},
  {"path": "tools/build.sh", "mode": "644", "content": "#!/bin/sh\n: \"${SITE_NAME:?Please export SITE_NAME first}\"\necho \"<h1>$SITE_NAME</h1>\" > index.html\nfor f in text/*.txt; do\n  echo \"<p><a href=\\\"$f\\\">$f</a></p>\" >> index.html\ndone\n# TODO: add a line that prints Build done!\n"}
]
```

**Step 1 — Make the site folders and move the images**
- Do: Create `site/images` and `site/text`, then move all `.jpg` and `.png` files from
  `downloads` into `site/images`.
- Check: `{"type": "all", "checks": [{"type": "dir_exists", "path": "site/text"}, {"type": "file_exists", "path": "site/images/band.jpg"}, {"type": "file_exists", "path": "site/images/logo.png"}, {"type": "path_missing", "path": "downloads/band.jpg"}]}`
- Solution: `mkdir -p site/images site/text` then `mv downloads/*.jpg downloads/*.png site/images/`
- Hints: "mkdir -p can make several folders at once. mv can take many files." / "Use wildcards: downloads/*.jpg"
- Explain: wildcards like `*.jpg` save a lot of typing.

**Step 2 — Copy the text files**
- Do: Copy (not move!) all `.txt` files into `site/text`.
- Check: `{"type": "all", "checks": [{"type": "file_exists", "path": "site/text/setlist.txt"}, {"type": "file_exists", "path": "site/text/tour.txt"}, {"type": "file_exists", "path": "downloads/setlist.txt"}]}`
- Solution: `cp downloads/*.txt site/text/`
- Hints: "cp works with wildcards too." / "Type: cp downloads/*.txt site/text/"
- Explain: keeping the originals is a simple backup.

**Step 3 — Fix the build script**
- Do: Read `tools/build.sh`. Add the missing line that prints `Build done!` and make it executable.
- Check: `{"type": "all", "checks": [{"type": "file_contains", "path": "tools/build.sh", "text": "Build done!"}, {"type": "file_mode", "path": "tools/build.sh", "mode": "755"}]}`
- Solution: `echo 'echo "Build done!"' >> tools/build.sh` then `chmod 755 tools/build.sh`
- Hints: "cat tools/build.sh to read it. Add a line with echo '...' >>" / "Then: chmod 755 tools/build.sh"
- Explain: reading other people's scripts before running them is a great habit.

**Step 4 — Build the site**
- Do: Set `SITE_NAME` to your band's name, go into `site`, and run `../tools/build.sh`.
- Check: `{"type": "all", "checks": [{"type": "output_contains", "text": "Build done!"}, {"type": "file_contains", "path": "site/index.html", "text": "text/setlist.txt"}]}`
- Solution: `export SITE_NAME="The Terminal Cats"` then `cd site` then `../tools/build.sh`
- Hints: "If you see 'Please export SITE_NAME first', the script is telling you what to do!" / `Type: export SITE_NAME="My Band"   then: cd site   then: ../tools/build.sh`
- Explain: the script used your variable and a loop to write HTML for you.

**Step 5 — Serve it and look**
- Do: Start a server on port 8765 (in the background, only for this computer) and get the main page with `curl`.
- Check: `{"type": "all", "checks": [{"type": "command_matches", "pattern": "^curl\\b"}, {"type": "output_contains", "text": "<h1>"}, {"type": "output_contains", "text": "setlist.txt"}]}`
- Solution: `python3 -m http.server 8765 --bind 127.0.0.1 &` then `curl http://127.0.0.1:8765/`
- Hints: "Look back at lesson 12." / "Make sure you are in the site folder when you start the server."
- Explain: you built and served a website using only the terminal!

**Step 6 — Clean up**
- Do: Stop your server.
- Check: `{"type": "command_matches", "pattern": "^(kill\\s+(-[A-Z0-9]+\\s+)?\\d+|pkill\\s+-f\\s+['\"]?\\S*http)"}`
- Solution: `pkill -f http.server`
- Hints: "Find the PID with ps aux | grep http.server, then kill it." / "Or type: pkill -f http.server"
- Explain: congratulations — you finished Terminal Academy! Ideas for next steps: learn
  an editor (`nano`), `git`, and try `ssh` on a Raspberry Pi or a free cloud server.

---

## 4. Safety and cross-platform notes

### 4.1 Safety

The sandbox is a **teaching guard, not a security sandbox**. The student runs commands
as their own user. Our job is to stop accidents, not hackers. Rules:

1. **Run as a normal user.** If the app is started as root (`os.geteuid() == 0`), print a
   warning and refuse to start (or ask twice). Also, permission lessons do not work as
   root (root can read everything).
2. **Blocklist** (checked on the whole line before running; print a friendly reason,
   e.g. "This command can damage a computer, so it is blocked in Terminal Academy."):
   - `sudo`, `su`, `doas` — no admin rights.
   - `shutdown`, `reboot`, `halt`, `poweroff`, `init 0`, `init 6`.
   - Disk tools: `mkfs`, `dd`, `fdisk`, `diskutil`, `parted`, writing to `/dev/sd*`,
     `/dev/disk*`, `/dev/nvme*`.
   - `rm` on `/`, `/*`, `~`, `~/`, `$HOME`, `.`, `..` or `*` at the sandbox root with `-r`
     (message for `~`: "That would delete your whole sandbox. Use `reset` instead.").
   - Fork bomb pattern `:(){`, and `chmod`/`chown -R` on `/` or system folders.
   - `curl ... | sh` / `| bash` (running code from the internet).
   - `kill -1`, `kill -9 -1`, `killall` (they stop many programs at once).
   - System config: `systemctl`, `launchctl`, `crontab`, `passwd`, `chsh`.
   - Remote access: `ssh` to a host, `scp`, `sftp`. **Allowed:** `ssh -G` and `ssh -V`
     (they do not connect), and `ssh-keygen`.
   - Writing outside the sandbox: for `rm`, `mv`, `cp`, `touch`, `mkdir`, `chmod`, `ln`
     and `>`/`>>` redirections, split the line with `shlex`, resolve each path argument
     (from the current folder, with `~` = sandbox) and block if it is outside the sandbox.
     Reading outside is allowed (`cat /etc/hosts`).
   Example regexes (Python, applied with `re.search`):
   ```
   (^|[;&|(]\s*)(sudo|su|doas)\b
   \b(shutdown|reboot|halt|poweroff)\b
   \b(mkfs\S*|fdisk|diskutil|parted)\b|\bdd\b.*\bof=
   :\(\)\s*\{
   \b(curl|wget)\b.*\|\s*(ba|z)?sh\b
   \bkill\s+(-\S+\s+)?-1\b|\bkillall\b
   \b(systemctl|launchctl|crontab|passwd|chsh)\b
   (^|[;&|(]\s*)(scp|sftp)\b
   ```
   The blocklist can be fooled (e.g. with variables). That is OK — it is for accidents.
3. **`HOME` = sandbox**, so `cd`, `~`, `~/.ssh` stay inside the sandbox.
4. **Leaving the sandbox:** if `cd` ends outside the sandbox, move the student back.
5. **Timeout** of 30 s for foreground commands; **stop all background processes** of a
   lesson when the student leaves it.
6. **Servers listen on `127.0.0.1` only** (`--bind 127.0.0.1`), never on all interfaces.
7. **Never ask for passwords.** No real remote servers. SSH keys are made only inside the
   sandbox. Teach: never share a private key; real keys should have a passphrase.
8. **No internet needed.** Every lesson works offline. Online examples are only mentioned
   in `explain` texts.
9. `stdin` is `/dev/null`, so nothing waits forever for keyboard input (except the
   interactive programs listed in 2.9).

### 4.2 Cross-platform pitfalls (macOS BSD tools vs Linux GNU tools)

Lesson writers must only use commands that work on both. Known traps:

| Avoid | Why | Use instead |
|-------|-----|-------------|
| `sed -i 's/a/b/' f` | macOS needs `sed -i '' ...`; GNU does not | `sed 's/a/b/' f > f.new && mv f.new f`, or `>>` / `echo` |
| `ls --color`, `ls --help` | GNU only | plain `ls`; `man ls` |
| `cmd --help` in general | many BSD tools don't have it | `man cmd` (and say "--help works for many, not all") |
| `grep -P` | GNU only | `grep -E` |
| `find -name x` without path, `find -printf` | BSD needs a path; `-printf` is GNU only | `find . -name x` |
| `stat -c` / `stat -f` | different on each | `ls -l` (the engine uses Python `os.stat`) |
| `date -d "yesterday"` | GNU only | `date +%A`, `date +%Y-%m-%d` |
| `echo -e "a\nb"` | `echo` handles `\n` differently in bash/sh/macOS | `printf 'a\nb\n'` |
| `head -n -3`, `tac` | GNU only | `tail -n`, `tail -r` is BSD only — avoid both |
| `readlink -f`, `realpath` | missing on older macOS | not needed in lessons |
| `xargs -r`, `cp --parents`, `du --max-depth` | GNU only | avoid; `du -d 1` works on both |
| `timeout 5 cmd` | not on macOS | the engine has its own timeout |
| `md5sum`, `sha256sum` | not on macOS (`md5`, `shasum -a 256`) | avoid in lessons |
| `ip`, `ss`, `hostname -I`, `ifconfig` | Linux only / macOS only / may be missing | `hostname`, `cat /etc/hosts` |
| `netstat`, `nc`, `lsof` | flags differ or may be missing | optional steps only |
| `ping` without `-c` | never stops | `ping -c 2 host` (works on both); still mark optional |
| `ps --sort`, `ps -o` GNU columns | GNU only | `ps`, `ps aux` (works on both), `ps -ef` (both) |
| `wc -l` exact output | macOS pads with spaces (`      20 file`) | check with `output_contains "20"` |
| bash 4+ features (`declare -A`, `${x,,}`, `mapfile`) | macOS ships bash **3.2** | simple POSIX `sh` syntax in all lesson scripts |
| `#!/bin/bash` in lesson scripts | path exists, but sh is simpler | `#!/bin/sh` |
| Names that differ only by case (`File.txt`, `file.txt`) | macOS disk is usually case-insensitive | always use different names |
| `/tmp` paths in checks | on macOS `/tmp` → `/private/tmp` | sandbox-relative paths; compare with `realpath` |

**Other notes**

- On macOS the user's login shell is `zsh`, but the app always runs `bash` (or `sh`), so
  lessons behave the same. Mention this in lesson 1 or 2 only if a student asks.
- `"#!..."` inside **double quotes** in a real interactive bash may trigger history
  expansion (`!`). Lessons always use **single quotes** for script lines.
- `sort` order can depend on the language settings (locale). Our lessons only sort simple
  names that start with capital letters, which sort the same everywhere. The engine can
  also set `LC_ALL=C` for commands to be sure.
- `python3 -m http.server --bind` needs Python 3.4+ (we require 3.9). Newer Python may
  print the address as `::` or `127.0.0.1`; checks never depend on this text.
- `ssh-keygen -t ed25519` works on macOS and modern Linux (OpenSSH 6.5+). `ssh -G` needs
  OpenSSH 6.8+ — that step is optional.
- Minimal Linux systems (e.g. Docker images) may not have `man`, `ping`, `curl`, `ssh` or
  `/etc/services`. Those steps/lessons use `requires` or `optional`, so the student can
  continue.
