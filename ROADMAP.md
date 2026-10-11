# Roadmap

Ideas for after v3.0.0, grouped by priority. Nothing here is promised; it is
a list to choose from. "Why" explains the value, so you can decide quickly.

## Priority 1 — Make v1 really good (do these first)

- **User testing with real teens.** Watch 2–3 beginners do lessons 1–5. Fix
  confusing texts and hints. *Why:* the lessons were written and tested by
  machines; real people will find problems no test can.
- **First real Mac run.** Play all 15 lessons on macOS with Apple's Python.
  *Why:* CI checks that steps are solvable, not that the text matches what a
  Mac prints (e.g. `ps`, `jobs` output).
- **Small engine polish:** hide bash's `Terminated` line after a timeout;
  make `clear` safe when there is no terminal; pick a free port automatically
  in lessons 12/15 (or detect "Address already in use" with a friendly hint).
- **Create the `lesson` label** on GitHub (used by the lesson-idea issue form).

## Priority 2 — More learning value

- **New lessons:** archives (`tar`, `zip`), data with `sort`/`uniq`/`cut`,
  `git` basics (init, add, commit, log — all local), text editors (`nano`),
  `history` and shortcuts (Ctrl+R, Tab), file links (`ln -s`), disk usage
  (`du`, `df`).
- **"Why does this work?" reflection questions** after some steps (the idea
  of the old CLI's "explanation gate", but optional and multiple-choice).
- **Challenge mode:** the same lesson without hints, for repeating.
- **Lesson map in the terminal:** a small ASCII "skill tree" showing levels
  and unlocked lessons (idea from the old desktop app).
- **More `explain` notes** and `explain` for options (`explain ls -l`).

## Priority 3 — Reach more people

- **Translations (Russian first).** Needs a design: lesson text per language
  (`lessons/ru/*.json`?) and UI strings in a dictionary. Keep English as the
  fallback.
- **Easier install:** `pipx install terminal-academy`, a Homebrew formula, or
  a one-line `curl … | sh` installer (only with a checksum and a clear
  explanation of what it does).
- **Teacher mode:** export progress as a small report (local file only).
- **Windows via WSL:** document and test.

## Priority 4 — Big ideas (need serious design)

- **Real isolation:** optional Docker/Podman sandbox for advanced lessons
  (users, packages, services, firewall) that need root inside a container.
  Only opt-in; the default must keep working without Docker.
- **Optional AI hints:** only opt-in, with a clear privacy notice, never
  sending file contents; or a local model. Must be safe for minors.
- **Server track:** a tiny local "remote" (e.g. an SSH server in a container)
  so lessons 13–14 can do a real `ssh` login.

## Not planned

- Accounts, cloud sync, ads, tracking, paid tiers.
- Bringing back the desktop app.
