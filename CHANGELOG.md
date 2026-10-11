# Changelog

All notable changes to this project are written here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-10-11

The big rework: Terminal Academy is now one small command-line app with real,
hands-on lessons. Details and reasons: `REWORK_LOG.md`.

### Added
- New CLI package `terminal_academy/` and launcher `./academy`
  (macOS + Linux, Python 3.9+, standard library only).
- Real commands run with `bash` in a per-lesson sandbox folder; `HOME` points
  to the sandbox; current folder and exported variables are kept between
  commands; 30-second timeout; background processes are stopped when you
  leave a lesson.
- 15 lessons (JSON): first steps, moving around, files and folders, reading
  files, searching, pipes and redirection, permissions, first script,
  variables and PATH, processes, network basics, local web server, SSH keys,
  SSH config, mini project.
- Automatic checks (9 check types), hints, `skip` (runs the solution),
  `reset`, `explain <command>` (offline notes), progress saved in
  `~/.terminal-academy/progress.json`.
- Blocklist of dangerous commands (`sudo`, `rm -rf /`, fork bomb, `shutdown`,
  `curl | sh`, …); the app refuses to run as root unless `--allow-root`.
- Command-line options: `list`, `start N`, `reset [N]`, `--version`,
  `--no-color`, `--home DIR`, `--allow-root`.
- Test suite (`unittest`, 159 tests) including a self-test that solves every
  lesson step; GitHub Actions CI on Ubuntu and macOS (Python 3.9 and 3.13,
  plus Apple's system Python).
- Brand identity (t//a logo, colors, fonts, favicons, app icons, brand guide)
  and a static landing page in `site/` with a GitHub Pages workflow.
- Branded CLI: big gradient logo, short boot animation, welcome screen.
- Open-source files: MIT `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, issue forms and a PR template.
- Project documents: `AUDIT.md`, `LESSONS_PLAN.md`, `REWORK_LOG.md`,
  `HANDOFF.md`, `ROADMAP.md`.

### Removed
- Tauri desktop app (`terminal-academy-desktop/`), including the Gemini AI
  mentor, the remote SSH/Docker sandbox, fake JWT login and fake system
  monitor.
- Old curses CLI (`cli-client/`) with its simulated shell, fake eBPF/Presidio
  layers and pricing tiers.
- Old Vite landing page (`web-landing/`), `docker-compose.yaml`, the desktop
  release workflow.

### Fixed (in the old CLI, before it was replaced)
- Crash on terminal resize; Python 3.9 incompatibility; `exit` not working
  while the explanation gate was armed.

### Security
- Removed a hardcoded root SSH login to a private server and the silent
  fallback to the host shell from the desktop app. The old code is still in
  git history.

## Before 1.0.0

Versions up to 2.1.1 were the Tauri desktop app. They are not compatible
with 1.0.0 and are not maintained. (The version number was reset to 1.0.0
because the new CLI is a new product. Note: an old git tag `v1.0.0` already
exists on a desktop commit; see `HANDOFF.md` §6 before tagging.)
