# Changelog

All notable changes to this project are written here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [3.1.0] — 2026-11-22

Part 2: Ethical Hacking. The 15 terminal lessons stay exactly as they were
(Part 1); this release adds an optional, Docker-based "capture the flag" track
with a live diagram page in the browser.

### Added
- **Part 2 · Ethical hacking** (`academy hack ...`): Docker-based levels that
  run in Debian-slim containers on an isolated, internet-less network. New
  package `terminal_academy/hacklab/` (Docker wrapper, flag store, event
  parsing, level loader, lab orchestrator, diagram server).
- **Three levels** (`terminal_academy/hacklab/levels/`), each with a story,
  objective, hints, Dockerfile(s), a diagram definition and a `LEARN.md`
  (concept, commands, and how defenders prevent the attack):
  1. *Hidden in Plain Sight* — hidden dotfiles; live filesystem-tree diagram.
  2. *Permission Denied* — rwx bits and a world-readable backup; permission-bit
     diagram.
  3. *Knock Knock* — `nmap` scan, SSH, dictionary attack from a small wordlist;
     live TCP-handshake and login-attempt diagram.
- **Live diagram page**: a standard-library web server with Server-Sent Events
  and one HTML page of clean SVG diagrams, fed by a shell hook in the player
  container and by `tcpdump` in the target container (network levels).
- **Random per-run flags**: a fresh `FLAG{...}` is generated each run and copied
  into the container at run time. The host stores only the SHA-256 hash — never
  the flag, never in an environment variable, never in the repo.
- Commands: `academy hack [list|start|hint|learn|submit|stop]`.
- Tests for flag checking, event parsing, level loading and validation, the
  diagram server (SSE), and the `hack` CLI.
- Ethics disclaimer (README): practice only inside this lab, never on systems
  you do not own.

### Notes
- Part 1 is unchanged and still standard-library only; it never needs Docker.
- Part 2 fails with a clear message when Docker is missing. On macOS 12, where
  Docker Desktop may be unsupported, the README documents Colima.

## [3.0.0] — 2026-10-11

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

## Before 3.0.0

Versions up to 2.1.1 (tags `v1.0.0`…`v2.1.1`, `v2.0.0-desktop`) were the
Tauri desktop app. They are not compatible with 3.0.0 and are not
maintained. 3.0.0 is the first version of the new command-line app.
