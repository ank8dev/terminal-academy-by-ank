# Handoff — Terminal Academy v3.0.0

This file is the "save point" of the project. Read it first when you come
back after a break. It tells you what exists, how it works, what was left
out on purpose, and what to do next.

---

## 1. Current state (November 2026)

- **Version:** 3.1.0 (see `terminal_academy/__init__.py` and `CHANGELOG.md`).
  v3.0.0 is the last tag; v3.1.0 adds Part 2.
- **What it is:** a command-line app that teaches teenagers and beginners the
  terminal. **Part 1:** 15 hands-on lessons, from `pwd` to SSH keys and a mini
  project (standard library only, no Docker). **Part 2:** optional Docker-based
  ethical-hacking "capture the flag" levels with a live browser diagram
  (`academy hack ...`).
- **Runs on:** macOS and Linux, Python 3.9+, standard library only. Part 2 also
  needs Docker (Colima on macOS 12).
- **Tests:** 225 `unittest` tests, all green on Linux with Python 3.13 (about
  25 s). The Part 2 tests that need Docker are the end-to-end solves, which are
  **not** in the `unittest` suite (see §5); the suite itself needs no Docker.
  CI runs the suite on Ubuntu and macOS for every pull request.
- **Status:** finished and released (v3.0.0). Website: https://ank8dev.github.io/terminal-academy-by-ank/ . **Not yet tried by a real student
  and not yet run on a real Mac** (only in CI) — see "Known problems".

What was removed in the rework (it lives only in git history now): the Tauri
desktop app, the old curses CLI (`cli-client/`), the old Vite landing page
(`web-landing/`), `docker-compose.yaml`. The reasons are in `REWORK_LOG.md`.

## 2. How to run

```sh
./academy                 # main menu
./academy list            # lessons and progress
./academy start 3         # start lesson 3
./academy --version
python3 -m unittest discover -s tests      # run all tests
```

Useful while developing:

```sh
# Keep your own progress clean: use a throw-away home folder
TERMINAL_ACADEMY_HOME=/tmp/ta-dev ./academy

# Play a lesson from a script (no keyboard needed)
printf 'pwd\nls\nquit\n' | NO_COLOR=1 TERMINAL_ACADEMY_HOME=/tmp/ta-dev ./academy start 1

# Self-test all lessons (each step must fail before and pass after its solution)
python3 -c "from terminal_academy import lessons as L; ls,e=L.load_lessons(); print(e); [print(l['id'], L.run_solution_check(l)) for l in ls]"
```

The app refuses to run as `root`. In a container that runs as root, set
`TERMINAL_ACADEMY_ALLOW_ROOT=1` (the tests do this themselves).

## 3. Architecture

```
academy                 POSIX sh launcher: finds python3 (>= 3.9), runs the package
terminal_academy/
  cli.py                command-line options (argparse) and the main menu
  engine.py             one lesson session: step loop, hint/skip/reset/menu/quit/explain
  shell.py              runs ONE student command in bash inside the sandbox
  checks.py             the 9 check types (file_exists, output_contains, cwd_is, ...)
  lessons.py            load + validate lesson JSON, set up sandbox, self-test helper
  safety.py             blocklist of dangerous commands (sudo, rm -rf /, fork bomb...)
  progress.py           progress.json (atomic write, broken file -> .bak)
  explain.py            offline notes for `explain <command>`
  ui.py                 colors, text wrapping, logo, Ank's messages
  lessons/*.json        the 15 lessons (data, no code)
tests/                  unittest suite (one file per module + lesson self-test)
site/                   landing page + brand guide (site/brand/) + icons (GitHub Pages)
```

**The flow of one command** (the heart of the app):

1. Student types a line in `engine.py`.
2. If it is an in-app word (`hint`, `skip`, …) → handled by the engine.
3. Else `safety.check_command()` → if dangerous, refuse with a friendly reason.
4. Else `shell.Shell.run()` starts a **new** `bash -c WRAPPER` process:
   - `HOME` = the lesson sandbox (`~/.terminal-academy/sandbox/<lesson-id>/`);
   - the wrapper loads the saved environment, `cd`s to the saved folder,
     runs the command with `eval`, and on exit saves `pwd` and `export -p`;
   - output goes to temp files (not pipes), 30 s timeout, own process group.
5. `checks.evaluate()` runs the current step's check against the sandbox
   and the last command/output. Pass → show `explain`, next step, save progress.

**Where data lives:** `~/.terminal-academy/progress.json` and
`~/.terminal-academy/sandbox/` (override with `--home` or
`TERMINAL_ACADEMY_HOME`).

**Lesson format:** documented in `LESSONS_PLAN.md` §2. The validator in
`lessons.py` is the strict version of that spec.

### Part 2 (ethical hacking) — `terminal_academy/hacklab/`

```
hacklab/
  docker_lab.py     thin wrapper over the `docker` CLI (build/run/exec/cp/...)
  flags.py          random FLAG{...}, SHA-256, host keeps only the hash
  events.py         pure parsers: shell hook, tcpdump, sshd auth log
  levels.py         load + validate level.json (like lessons.py for Part 1)
  session.py        the orchestrator: build images, start containers on an
                    --internal network, place the flag, feed the diagram
  diagram_server.py stdlib HTTP + Server-Sent Events
  diagram.html      one page, SVG diagrams, updates over SSE
  rc.sh             the shell hook mounted into the player container
  cli.py            the `academy hack ...` subcommands
  levels/<id>/      level.json + Dockerfile.* + LEARN.md
```

**Reuse of Part 1:** the `UI`, the `Progress` file (new keys per level), and the
hint-first style are shared. The flag check plays the role of a Part 1 "check".
The lesson-loader pattern (strict validator, self-testing) is mirrored in
`levels.py`.

**Flow of a level:** `session.start()` builds images, creates an internal
network, runs each container with `/lab` bind-mounted (hook + event files),
generates a flag and `docker cp`s it into the container, and (network levels)
starts `tcpdump` on the target. `session.snapshot()` builds the diagram state
(reading the event files and, for filesystem/permission views, a fresh
`docker exec` snapshot). `diagram_server` polls `snapshot()` and pushes JSON to
the page over SSE.

**Build network note:** a build/run env var `TERMINAL_ACADEMY_BUILD_NETWORK`
(e.g. `host`) lets the Docker build reach the package mirror through the host's
network. Normal users leave it unset; it exists for sandboxes behind an HTTPS
proxy (such as the cloud CI box this was built in).

## 4. Consciously NOT done (and why)

| Not done | Why |
|----------|-----|
| Real isolation (containers, VMs) | Needs Docker or root; too heavy for teens on their own laptop. The sandbox is a folder + blocklist; it prevents accidents, not attacks. |
| AI mentor (Gemini etc.) | Privacy of minors, API keys, network. All hints are pre-written and offline. |
| Windows support | Lessons teach Unix tools; Windows users can use WSL. Not tested there. |
| Russian / other languages | English first. The old `translation_ru.json` was dropped with the desktop app. Needs an i18n design (see ROADMAP). |
| pip / Homebrew package | `git clone` + `./academy` is enough for now. |
| Keeping the desktop app | Security problems and a fake sandbox (see `AUDIT.md` §5). Useful ideas were ported. |
| `jobs`/`fg` across lines | Each command is a new bash process, so jobs only exist within one line. Explained in lesson 10. |

## 5. Known problems

0. **Part 2 tested on Linux + Docker only.** All three levels were built and
   solved end to end in containers on Linux (Docker Engine 29), and the live
   diagram was confirmed reacting over SSE. **Not** yet run on macOS/Colima, and
   the end-to-end container solves are **not** part of the `unittest` suite
   (they need a Docker daemon and take minutes). The suite covers the pure
   logic (flags, event parsing, level loading/validation, the diagram server,
   the `hack` CLI) without Docker. The `docker exec` snapshot for the
   filesystem/permission diagrams uses GNU `find -printf` and `stat -c`, which
   is correct inside the Debian containers regardless of the host OS.
1. **Never run on a real Mac by a human.** CI covers macOS (incl. Apple's
   Python 3.9 and bash 3.2), but output details (`ps`, `jobs`) may differ.
2. **CI matrix uses `macos-15-intel`** for Python 3.9. If GitHub renames or
   retires this runner, the job waits forever — change the matrix.
3. **Fixed ports** 8765 (lesson 12) and 8766 (lesson 15). Two test runs at the
   same time on one machine can collide; a student with something on those
   ports gets "Address already in use" (the lesson text mentions it).
4. **Blocklist is pattern-based.** `eval`, variables or quoting tricks can
   get around it. Fine for accidents; not a security boundary.
5. **`clear` without a terminal** prints raw escape codes (only in piped mode).
6. **On timeout**, bash's own `Terminated` line can appear in the output.
7. **Lesson 15 solution** finds the server with `ps | grep "http.server 8766"`;
   on a machine where another process has the same text it could stop that one.
8. **Steps that need `ping`, `ssh-keygen`, `curl`, `pgrep`** are auto-skipped
   when the tool is missing; those students see less of lessons 11–15.
9. **Slow reverse DNS on GitHub's Apple Silicon runners.** There,
   `socket.getfqdn("127.0.0.1")` takes 35 s, and `python3 -m http.server`
   calls it before it starts listening, so lessons 12 and 15 hang. CI works
   around it with a tiny `sitecustomize.py` (see `ci.yml`). A real Mac with a
   normal network should not have this, but if a student's server takes very
   long to start, this is the reason. Check on a real Mac.
10. **Security note from the audit:** the old desktop code (still in git
   history) contained a root SSH login to a private server IP. The owner
   should check / rotate access to that server.

## 6. How to continue (first steps for the next session)

1. **Check that everything is still green:** CI on `main` (Actions tab) and
   the website (https://ank8dev.github.io/terminal-academy-by-ank/). Nothing else is required — the project is
   in a finished state.
2. **Test with a real person on a real Mac.** Give lessons 1–5 to one teen,
   watch silently, write down every place they get stuck. Fix texts/hints
   first — this is the cheapest, highest-value improvement.
3. **Website:** it deploys automatically from `main` (`.github/workflows/pages.yml`
   → branch `gh-pages`) whenever `site/` changes. If a logo SVG in
   `site/brand/` changes, re-render the PNG/ICO icons (see `site/README.md`).
4. **Fix the small engine issues** from "Known problems" 5–6 (hide
   `Terminated`, make `clear` safe without a terminal) — each is a small,
   well-tested change in `shell.py`.
5. **Write the next lesson** using the "How to add a lesson" section in
   `CONTRIBUTING.md` (ideas: `tar`/archives, `sort`/`uniq` data lesson,
   `git` basics). The self-test will tell you immediately if it is solvable.

See `ROADMAP.md` for the bigger ideas.
