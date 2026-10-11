# t//a — Terminal Academy

**Learn the terminal by typing real commands, in a safe practice folder.**

## What it is

Terminal Academy is a free, open-source app that teaches you how to use the
terminal (also called the command line). It runs in your own terminal. Each
lesson gives you small tasks, like "make a folder called projects". You type
real commands, and the app checks your work, gives hints when you are stuck,
and explains what you just did.

Everything happens inside a practice folder (the *sandbox*), so you can try
things without being afraid of breaking your computer.

## Who it is for

- **Teens (13–18)** who are curious about how computers really work.
- **Beginners of any age** who have never opened a terminal, or always felt a
  bit lost in one.
- **Parents and teachers** who want a free, offline tool to give to a learner.
  No account, no ads, no tracking.

## Features

- **Real commands in a safe sandbox.** You use the real `bash` on your
  computer, inside a lesson folder. Your home folder (`~`) points to the
  sandbox too.
- **Automatic checks.** The app sees when a step is done and moves on.
- **Hints.** Type `hint` for a clue; type it again for the next one.
- **Progress saved locally.** Stop at any time and continue later.
- **Works offline.** No internet connection is needed.
- **No account, no tracking.** The app never sends anything anywhere.
- **`explain <cmd>`.** Short, friendly notes about common commands
  (for example `explain ls` or `explain grep`).

## Requirements

- **macOS or Linux**
- **Python 3.9 or newer** (only the standard library — nothing to `pip install`)
- **bash** (comes with macOS and Linux; the app falls back to `sh` if bash is missing)

Check your Python version with `python3 --version`.

## Install and run

```sh
git clone https://github.com/ank8dev/terminal-academy-by-ank.git
cd terminal-academy-by-ank
./academy
```

`python3 -m terminal_academy` (run from the project folder) does the same as
`./academy`.

## Example session

This is real output from `./academy start 1` (shortened; your sandbox path
will be different):

```text
Lesson 1 · First Steps
──────────────────────
The terminal is a way to talk to your computer with text.
You type a command, press Enter, and the computer answers.
...
Type help to see what you can do, or hint if you get stuck.

Step 1 of 5
ank › Where am I? Type pwd and press Enter to see which folder you are in.
academy:~ $ pwd
/home/you/.terminal-academy/sandbox/01-first-steps
✓ You got it!
ank › The working directory is the folder you are 'standing in' right now. That
      long path is your sandbox: your own safe practice folder.

Step 2 of 5
ank › What is here? List the files and folders in this folder.
academy:~ $ ls
hello.txt
music
photos
✓ That's the one!
...

Step 3 of 5
ank › Make the computer talk: print the text Hello, terminal!
academy:~ $ hint
ank › Hint 1/2: echo repeats what you give it.
academy:~ $ echo "Hello, terminal!"
Hello, terminal!
✓ Nice!
ank › echo prints text. The quotes keep the words together as one piece of text.

Step 4 of 5
ank › Your screen is getting full. Clear it.
academy:~ $ explain echo
ank › echo prints the text you give it. It is great for quick messages, and
      together with > it can write text into a file: echo hi > note.txt
academy:~ $ sudo ls
Blocked: Terminal Academy never needs admin rights, so sudo, su and doas are
blocked. Everything you need works as a normal user.
academy:~ $ quit
ank › Progress saved. See you next time!
ank › Bye! Come back soon.
```

## Commands inside a lesson

These only count when you type the word alone on the line. Everything else
is a real command and runs in your sandbox.

| Command         | What it does |
|-----------------|--------------|
| `hint`          | Show a clue. Type it again for the next clue. |
| `skip`          | Skip this step (asks first). Shows a solution and runs it for you, so the next step works. |
| `reset`         | Start the lesson again with a fresh sandbox (asks first). |
| `explain <cmd>` | A short note about a command, e.g. `explain ls`. `explain` alone lists all topics. |
| `lessons`       | Show all lessons and your progress. |
| `menu`          | Go back to the main menu. Your progress is saved. |
| `help`          | Show the current task again and this list of commands. |
| `quit`          | Save and exit. `exit` and `Ctrl+D` do the same. |

`Ctrl+C` stops a command that is running. At an empty prompt it does not quit;
it reminds you to type `quit`.

## Command-line options

```sh
./academy                 # main menu
./academy list            # list lessons and your progress
./academy start 3         # start lesson 3 (a number or an id like 03-files-and-folders)
./academy reset           # forget ALL progress (asks first)
./academy reset 3         # forget progress in lesson 3 only
./academy reset 3 -y      # ... without asking
./academy --version       # print the version
./academy --help          # show all options
```

Options that work with every command:

| Option         | Meaning |
|----------------|---------|
| `--no-color`   | Do not use colors. Setting the `NO_COLOR` environment variable works too. |
| `--home DIR`   | Keep progress and sandboxes in `DIR` instead of `~/.terminal-academy`. The `TERMINAL_ACADEMY_HOME` environment variable works too. |
| `--allow-root` | Run even as root (not recommended, see below). |

## Lessons

| #  | Lesson            | Level | Time    | What you learn |
|----|-------------------|-------|---------|----------------|
| 1  | First Steps       | 1     | ~5 min  | Meet the terminal: pwd, ls, echo, clear and how to get help. |
| 3  | Files and Folders | 1     | ~8 min  | Create, copy, move and delete files and folders. |

More lessons are listed in [LESSONS_PLAN.md](LESSONS_PLAN.md) and will be
added soon. Lessons are JSON files in `terminal_academy/lessons/`; when you
add one, add a row to this table too (`./academy list` shows the same info).

## Safety notes

- **Sandbox.** Every lesson has its own folder in
  `~/.terminal-academy/sandbox/<lesson>`. Commands start there, and `HOME`
  is set to it, so `cd ~` stays inside. If you `cd` out of the sandbox,
  the app moves you back.
- **Blocklist.** Dangerous commands (like `sudo`, `rm -rf /`, a fork bomb,
  `shutdown`, or `curl ... | sh`) are blocked with a friendly explanation.
  Commands that would *change* files outside the sandbox are blocked too
  (reading them, like `cat /etc/hosts`, is fine).
- **The blocklist prevents accidents. It is not real security.** Commands
  run as your own user, and a determined person can get around any list of
  patterns. Do not use Terminal Academy to run code you do not trust.
- **Limits.** A command is stopped after 30 seconds. Background processes
  (like `sleep 300 &`) are stopped when you leave the lesson. Files you
  create are limited to 100 MB each.
- **No root.** The app refuses to run as root (the admin user), because a
  mistake as root can break the whole computer. Run it as your normal user.

## Project layout

| Path | What's there |
|------|--------------|
| `academy` | Launcher script (checks your Python, then starts the app) |
| `terminal_academy/` | The app: a Python package, standard library only |
| `terminal_academy/lessons/` | Lessons, one JSON file each |
| `tests/` | Unit tests (`unittest`) |
| `site/` | Static landing pages |
| `LESSONS_PLAN.md` | The lesson format and the plan for all lessons |
| `.github/workflows/` | CI (tests on Ubuntu and macOS) and the GitHub Pages deploy |

## Running tests

```sh
python3 -m unittest discover -s tests
```

The tests check every lesson file: it must be valid, and every step must be
solvable with its own `solution`. They use temporary folders and never touch
your real `~/.terminal-academy`. CI runs them on Ubuntu and macOS.

## Contributing

Ideas, bug reports, lessons and code are all welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) and our
[Code of Conduct](CODE_OF_CONDUCT.md). Security problems:
see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)

## Landing page

The `site/` folder has the project's landing page: plain HTML and CSS with no
build step. `site/index.html` links to three design variants (`v1/`, `v2/`,
`v3/`). It is published to GitHub Pages by `.github/workflows/pages.yml`
when `site/` changes on `main`. To preview it locally:

```sh
python3 -m http.server -d site
# then open http://localhost:8000
```
