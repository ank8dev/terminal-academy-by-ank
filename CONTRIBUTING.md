# Contributing to Terminal Academy

Thanks for wanting to help! Terminal Academy is a small CLI app that teaches
teenagers and beginners how to use the terminal. Every contribution counts,
big or small, and you don't need to be an expert to help.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before you start.
We want this to be a friendly place for everyone, especially beginners.

## Ways to contribute

- **Report a bug.** Something broken or confusing? [Open a bug report](../../issues/new/choose).
- **Suggest a lesson.** Have an idea for something people should learn? Use the "Lesson idea" issue form.
- **Write a lesson.** Turn an idea into a real lesson (see [Adding a lesson](#adding-a-lesson)).
- **Improve the code.** Fix bugs, clean things up, or build new features.
- **Improve the docs.** Typos, unclear steps, missing info — all welcome.
- **Translations.** Not yet, but planned for later. Watch the issues if you want to help.

Not sure where to start? Look for issues labeled `good first issue`, or open an
issue and ask. Questions are always okay.

## Development setup

You need **Python 3.9 or newer**. That's it — Terminal Academy uses only the
Python standard library, so there is nothing to `pip install`.

```sh
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/terminal-academy-by-ank.git
cd terminal-academy-by-ank

# 2. Check your Python version
python3 --version

# 3. Run the app
./academy
# or
python3 -m terminal_academy
```

Project layout:

| Path | What's there |
| --- | --- |
| `terminal_academy/` | The app's source code (a Python package) |
| `terminal_academy/lessons/` | Lessons, one JSON file each |
| `tests/` | Unit tests |
| `LESSONS_PLAN.md` | The lesson format and the plan for upcoming lessons |

## Running tests

```sh
python3 -m unittest discover -s tests
```

Please run the tests before you open a pull request. CI (GitHub Actions) also
runs them on every pull request, on both **Ubuntu** and **macOS**.

## Adding a lesson

Lessons are JSON files in `terminal_academy/lessons/`. The full format is
described in [LESSONS_PLAN.md](LESSONS_PLAN.md).

1. **Check for an existing issue** or open a "Lesson idea" issue first, so
   nobody does the same work twice.
2. **Create the JSON file** in `terminal_academy/lessons/`. Copy an existing
   lesson as a starting point.
3. **Try it yourself.** Run `./academy`, play through your lesson from start to
   finish, and make some mistakes on purpose to check the hints.
4. **Run the tests** (`python3 -m unittest discover -s tests`). They check that
   every lesson file is valid.

Lesson rules:

- **Works on macOS and Linux.** Some commands behave differently (for example
  `sed -i`, `stat`, `date`, or `ls` flags). Use options that work on both, or
  avoid them. Test on both if you can — CI will help too.
- **No root.** Never require `sudo` or admin rights.
- **Safe commands only.** Lessons must never delete, change, or read files
  outside the lesson's practice area. No `rm -rf` on real folders, no network
  downloads, no changes to system settings.
- **Friendly language.** Our learners are often teenagers and total beginners.
  Use short sentences and simple words. Explain new terms. Be encouraging —
  mistakes are part of learning. No jokes at the learner's expense.
- **One idea per step.** Small steps are easier to learn from than big ones.

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Keep functions small and focused, with clear names.
- Type hints are welcome.
- **Standard library only.** Please don't add third-party dependencies. If you
  think one is really needed, open an issue to discuss it first.
- Code must work on Python 3.9, so avoid newer-only syntax (like `match`
  statements or `X | Y` type unions at runtime).
- Add or update tests when you change behavior.

## Commit messages

Write short messages in the imperative mood, like a command:

```
Add lesson about pipes
Fix crash when lesson file is empty
Update setup steps in README
```

Keep the first line under about 70 characters. Add more detail below a blank
line if needed.

## Pull request process

1. Create a branch for your change: `git checkout -b add-pipes-lesson`.
2. Make your change. Keep each pull request focused on one thing.
3. Run the tests.
4. Push your branch and open a pull request. Fill in the template.
5. A maintainer will review it. We may ask for changes — that's normal and not
   a bad sign!
6. Once CI passes and the review is approved, we'll merge it.

Thank you for helping people learn the terminal!
