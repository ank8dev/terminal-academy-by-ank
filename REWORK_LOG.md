# Rework log

This file explains, step by step, what was changed during the big rework of
Terminal Academy, **why** each decision was made, and what is still open for
discussion. It is written in simple English on purpose.

---

## Stage 0 — Preparation

**What was done**
- Created the branch `rework` from `main`. All work happens there; one PR
  goes from `rework` into `main` at the end.

**Decisions**
- Every stage is a separate commit (or a few commits), so you can read the
  history stage by stage with `git log --oneline main..rework`.
- Wave 1 tasks (audit, sites, lessons plan, open-source docs) touch
  different files, so they ran in parallel. Wave 2 tasks change the same
  code, so they ran one after another.

---

## Wave 1 (stages 1–4, done in parallel)

### Stage 1 — Audit (`AUDIT.md`)

**What was done:** a full read-through of the repository, with real checks
(running the CLI in a pseudo-terminal, building the desktop frontend).

**Most important findings (simple version)**
- The old CLI looked like a terminal, but it was a **fake shell**: commands
  like `ls` were never run. So no lesson was really hands-on.
- The old CLI **crashed when you resized the window**, and did not run on
  Python 3.9.
- Many features were **decoration only**: "eBPF", "Presidio", "gVisor",
  pricing tiers, login, random CPU numbers in the desktop app.
- **Security problem in the desktop app:** it had a hardcoded `root` SSH
  login to a private server IP and a key path from the author's laptop.
  For everyone else it silently used the **real host shell** as the
  "sandbox". It also sent every command and its output to Google Gemini.
  ⚠️ The server IP stays in git history even after we delete the code, so
  the owner should check/rotate access on that server.

**Decision:** the audit is the "map" for stage 5 (cleanup) and stage 6
(move to CLI).

### Stage 2 — Three landing pages (`site/v1`, `site/v2`, `site/v3`)

**What was done:** three static pages (only HTML + CSS, no JavaScript):
- v1 — retro green terminal style;
- v2 — clean, modern, light (with dark mode);
- v3 — playful "game levels" style.

**Decisions**
- No build tools (no npm, no Vite). A static page is easier to host and
  maintain; you can open `index.html` directly in a browser.
- All pages tell the same true facts (free, MIT, Python 3.9+, macOS/Linux,
  `./academy`), so whichever design you pick will not lie about the app.

**Open question:** v3 shows fun "badges". The app itself has no badges.
The page says they are just for fun, but you may want to remove them.

### Stage 3 — Lessons plan (`LESSONS_PLAN.md`)

**What was done:** a precise lesson format (one JSON file per lesson, a
fixed list of 9 "check types") and a plan of 15 lessons from level 1
(`pwd`, `ls`) to level 5 (SSH keys, mini project).

**Decisions**
- **JSON, not YAML.** Python can read JSON without extra libraries. We want
  zero dependencies.
- **Fixed small set of checks** (`file_exists`, `output_contains`,
  `cwd_is`, …). Lesson writers do not write Python code; they only describe
  what "done" looks like. This keeps lessons easy to write and to test.
- **Every step has a `solution`.** An automatic test runs every solution,
  so we know every lesson can really be finished.

**Open question (important):** the audit suggested that students type
commands in their *own* terminal and the app only checks the result. The
plan instead runs the commands *inside the app* (in a sandbox folder).
I chose the in-app way because:
1. the app can see the command and its output, so it can check more things
   and give better hints;
2. the app can block obviously dangerous commands before they run;
3. it is "one window", which is simpler for a 13-year-old.
The cost: it is not 100% the same as a real terminal (for example, `jobs`
only sees jobs started in the same line).

### Stage 4 — Open-source files

**What was done:** `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
(Contributor Covenant 2.1), `SECURITY.md`, issue forms (bug, feature,
lesson idea) and a PR template in `.github/`.

**Note:** these files describe the *target* project layout
(`terminal_academy/`, `./academy`, `tests/`), which is built in wave 2.
The issue forms use a `lesson` label — it may need to be created on GitHub.

---

## Wave 2 (stages 5–8, one after another)

### Stage 5 — Cleanup (based on `AUDIT.md`)

**What was done**
- Deleted files nobody used: `docker-compose.yaml`, `cli-client/Dockerfile.sandbox`,
  `cli-client/auth.py`.
- Removed fake code from the old CLI: fake "eBPF" and "Presidio" classes,
  pricing tiers, the disabled login screen, a duplicate copy of the
  cheat-word list, fake status lines ("gVisor active").
- Fixed real bugs: crash on window resize; Python 3.9 support; `exit` did
  not work while the "explanation gate" was waiting; typing a module number
  did nothing although the text said it should.
- Cleaned `.gitignore`. Important: it ignored **all `*.txt` files**, which
  would have hidden lesson files later.

**Decisions**
- The desktop app was **not** touched here (that is stage 6), as planned.
- I did **not** redesign the old CLI, because stage 6 replaces it. Cleanup
  first, then replace, gives two small, readable steps in git history
  instead of one huge one.

**Concept to understand — "dead code":** code that is never run or whose
result is never used. It is not harmless: people read it, believe it, and
waste time on it. Git keeps the history, so deleting is safe — you can
always find old code with `git log`.

### Stage 6 — Move to one CLI, delete the desktop app

**What was done**
- New package `terminal_academy/` (Python 3.9+, **standard library only**)
  and a launcher script `./academy` — one command to start on macOS/Linux.
- Modules, each with one job:
  - `shell.py` — runs the student's **real** commands with `bash` inside a
    sandbox folder (`~/.terminal-academy/sandbox/<lesson>`), remembers the
    current folder and exported variables between commands, stops commands
    after 30 s, kills forgotten background processes.
  - `checks.py` — the 9 check types from `LESSONS_PLAN.md`.
  - `lessons.py` — loads and validates lesson JSON; has a self-test helper
    that runs every step's `solution` and checks the step really passes.
  - `engine.py` — the lesson loop (`hint`, `skip`, `reset`, `menu`, `quit`…).
  - `safety.py` — blocks dangerous commands (`sudo`, `rm -rf /`, fork bomb…).
  - `progress.py` — saves progress to `progress.json`.
  - `explain.py` — offline `explain <command>` notes for ~40 commands.
  - `ui.py`, `cli.py` — colors, splash logo, menu, command-line options.
- Two lessons to prove the engine works: 01 and 03.
- Deleted: `terminal-academy-desktop/`, `cli-client/`, `web-landing/`,
  the desktop release workflow. GitHub Pages now publishes `site/`.

**What was moved from the desktop app (and what was not)**
- Moved: the dangerous-command list, the "reset sandbox" idea, the
  "explain this command" idea (now offline, no AI), the skill-tree idea
  (lessons are grouped by level).
- Not moved: Gemini AI mentor (privacy + API key + network), SSH to a
  private server, Docker, fake JWT login, fake monitoring.
- From the old CLI: the `t//a` logo and mentor "Ank" — but Ank is now kind
  to teens (no "kid"/"grandma" jokes).

**Decisions and why**
- **No curses, simple line-by-line UI.** Easier to test, works in any
  terminal, no resize crashes.
- **Every command runs in a new `bash` process**, and the app saves
  `pwd` and `export -p` after it. Simple and robust: a broken command
  cannot break the app.
- **`HOME` = sandbox folder**, so `cd ~` and `~/.ssh` stay inside the
  sandbox and never touch your real files.
- **The app refuses to run as `root`** (unless `--allow-root`), because a
  mistake as root can break the whole computer.

**Concept to understand — "process group":** when you start `sleep 300 &`,
it keeps running after the command line ends. The app starts every command
in its own *process group* (a family of processes with one id), so it can
stop the whole family later with one signal.

**Open questions**
- The blocklist prevents accidents, **not** attacks (variables or `eval`
  can trick it). For a teen learning tool on their own computer this is
  acceptable; real isolation (containers) is in the roadmap.
- Not tested on a real Mac yet — only written to be portable. CI (stage 7)
  runs on macOS to cover this.

### Stage 7 — Quality: tests, CI, README

**What was done**
- `tests/` — 156 tests with `unittest` (part of Python, no install needed).
  They cover all 9 check types, the shell runner (cd, export, timeout,
  background processes), the blocklist, progress saving, lesson
  validation, the command-line interface and a full scripted run of a
  lesson. The whole suite takes about 8 seconds.
- **The most important test** (`test_lessons.py`): for every lesson file it
  runs each step's `solution` and checks that the step fails *before* and
  passes *after*. New lessons are tested automatically — just add the JSON.
- `.github/workflows/ci.yml` — runs on every pull request: Ubuntu + macOS,
  Python 3.9 + 3.13, plus one job with the Python and bash that a normal
  Mac already has (Apple's `python3` and old bash 3.2).
- New `README.md`: what it is, for whom, install, a **real** example
  session (copied from a real run), commands, safety, layout, tests.

**Decisions and why**
- **`unittest`, not `pytest`.** pytest is nicer, but it is a dependency.
  The project rule is "standard library only".
- **The macOS "stock" job.** Students will not install a new Python. The
  most likely real setup is Apple's Python 3.9 and bash 3.2, so we test
  exactly that.

**Concept to understand — CI (Continuous Integration):** a robot (GitHub
Actions) runs the tests on clean machines for every pull request. If a
change breaks something on macOS, you see a red ❌ before merging, not
after a student complains.

**Open questions**
- macOS + Python 3.9 from `setup-python` runs on the Intel runner
  `macos-15-intel` (there is no Apple Silicon build of 3.9). If GitHub
  renames that runner, only the matrix needs a fix.

