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

