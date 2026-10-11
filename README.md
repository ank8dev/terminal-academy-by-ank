# t//a — Terminal Academy

A free, open-source app that teaches teenagers and beginners how to use the
terminal. You type real commands in a safe practice folder, and the app
checks your work, gives hints and explains what happened.

## Quick start

You need **macOS or Linux** and **Python 3.9 or newer**. Nothing to install.

```sh
git clone https://github.com/ank8dev/terminal-academy-by-ank.git
cd terminal-academy-by-ank
./academy
```

Useful commands:

```sh
./academy              # main menu
./academy list         # lessons and your progress
./academy start 1      # start lesson 1
./academy reset        # forget your progress
```

Your progress and practice folders live in `~/.terminal-academy/`.

## Repository layout

| Path | What's there |
| --- | --- |
| `academy` | Launcher script (checks your Python, then starts the app) |
| `terminal_academy/` | The app (a Python package, standard library only) |
| `terminal_academy/lessons/` | Lessons, one JSON file each |
| `site/` | Static landing pages (deployed to GitHub Pages) |
| `LESSONS_PLAN.md` | The lesson format and the plan for all lessons |

Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md). License: [MIT](LICENSE).
