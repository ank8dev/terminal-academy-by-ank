# Terminal Academy — Repository Audit

Branch: `rework` (commit `edcc295`). Audit date: 2026-10-11.
Scope: the committed tree (`git ls-files`). Line numbers refer to this commit.

How I tested (all builds were done in a copy at `/tmp/claude-0/audit-scratch`, nothing was installed inside the repo):

- `ast.parse` on `cli-client/*.py`. Imported `main.py` under Python 3.9, 3.11, 3.12 and 3.13.
- Called `process_command()`, `trigger_menu_choice()` and `KeystrokeAnalyzer` directly from a test script.
- Ran the real curses UI inside a Python pseudo-tty: typed text, pasted text, and resized the window.
- `ruff check` on the Python code.
- `npm ci`, `npm run build`, `oxlint`, `npm outdated` and `npm audit` for `terminal-academy-desktop/` and `web-landing/`.
- `cargo check` for `src-tauri/`. It could not finish: the GTK/WebKit system libraries are missing in this container. This is an environment limit, not a code finding.
- Network: npm and uv downloads worked. The GitHub API for this repo was blocked (403), so I could not check the names of the release assets.

---

## 0. Summary (TL;DR)

1. **The CLI does not run any real commands.** Every command except `help`, `status`, `clear` and `exit` prints `Command '...' not found` (tested: `ls -la`, `pwd`, `1`). "Executing" after the SOLO gate is only a log line (`main.py:1047-1048`). Today the "lessons" are text plus keyword matching. Nothing is hands-on.
2. **The CLI crashes when you resize the terminal.** `main.py:1728` unpacks 5 return values into 3 names. Reproduced in a pty: `ValueError: too many values to unpack (expected 3)`.
3. **The CLI does not work on Python 3.9.** It uses `str | None` without `from __future__ import annotations` (`main.py:63,129,670`). Reproduced: `TypeError: unsupported operand type(s) for |`. It runs on 3.11+.
4. **Many features are fake.** Fake "eBPF" and "Presidio" classes, a fake pricing/tier matrix, fake gVisor status text, fake login, fake system monitor numbers (`Math.random()`), a hardcoded mock JWT, and a mock Yoti age-verification SDK.
5. **The desktop app has serious security problems.** It hardcodes a root SSH login to a private server (`root@89.22.239.107`, key path `/Users/ank/.ssh/id_ed25519`) in 7 places in `lib.rs`. When SSH fails (which is the case for every user except the author), it opens **the user's real host shell** (`lib.rs:177-186`). The only protection is a client-side substring blacklist. Every command and its output are sent to Google Gemini.
6. **Good content to reuse:** `curriculum_linux.md` (20 nodes × 15 scenario ideas) is a strong source for teen exercises. The SOLO rubric questions in `main.py` can become "explain it" questions. Most of the DevOps, hosting and network content is too advanced or needs a server. Some network nodes are offensive-security material that does not suit teens.

---

## 1. Repository structure

```
.
├── README.md                     Root readme. Describes the desktop app only; partly false (see §2.4)
├── .gitignore                    Ignores start.sh, infra/, config.json, *.txt, token.* ...
├── docker-compose.yaml           gVisor (runsc) sandbox + Presidio sidecar. Not used by any code
├── .github/workflows/
│   ├── pages.yml                 Builds web-landing and deploys it to gh-pages (only on push to main)
│   └── release.yml               Builds Tauri installers for macOS/Linux/Windows on tag v*
├── cli-client/
│   ├── main.py                   1798-line curses TUI: menus, fake shell, SOLO gate, mentor text
│   ├── auth.py                   Fake token check + POST to api.terminal.academy. Never called
│   └── Dockerfile.sandbox        Alpine 3.18 image with user "student" (UID 10001)
├── terminal-academy-desktop/
│   ├── README.md                 Desktop readme (mentions the server IP and the config.json API key)
│   ├── index.html                Vite entry; loads the Yoti sandbox SDK + a mock Yoti with a fake JWT
│   ├── package.json / package-lock.json
│   ├── vite.config.ts, tsconfig*.json, .oxlintrc.json, .gitignore
│   ├── public/
│   │   ├── curriculum_linux.md     20 nodes × 15 incidents (Linux basics → troubleshooting)
│   │   ├── curriculum_network.md   20 nodes (iproute2, DNS, firewall, SSH, ... + offensive topics)
│   │   ├── curriculum_devops.md    20 nodes (Docker, Compose, CI/CD, Kubernetes, Helm)
│   │   ├── curriculum_hosting.md   20 nodes (systemd, nginx, Postgres, Redis, Minecraft servers)
│   │   ├── curriculum_graph.json   Skill-tree positions (33 nodes) + "edges" (edges are unused)
│   │   ├── blacklist.json          31 substrings that the desktop terminal blocks
│   │   ├── translation_ru.json     Russian UI strings (loaded but never shown, see §3.2)
│   │   ├── favicon.svg             Default Vite logo (used by index.html)
│   │   └── icons.svg               Social-icon sprite from the Vite template (unused)
│   ├── src/
│   │   ├── App.tsx               2476 lines: every widget, Gemini calls, layout engine
│   │   ├── App.css, index.css    Styles
│   │   ├── main.tsx              React root
│   │   └── assets/hero.png, react.svg, vite.svg   (all three unused)
│   └── src-tauri/
│       ├── src/lib.rs            PTY + remote Docker over SSH, fake JWT check (356 lines)
│       ├── src/main.rs           Calls app_lib::run()
│       ├── Cargo.toml / Cargo.lock / build.rs
│       ├── tauri.conf.json       productName "Terminal Academy", v2.1.1, CSP disabled (null)
│       ├── capabilities/default.json
│       └── icons/                ~60 icons incl. android/ and ios/ (no mobile build exists)
└── web-landing/
    ├── index.html                Marketing page + OS detection for desktop installer downloads
    ├── script.js                 Typewriter demo, particles, tilt effect, theme toggle, easter egg
    ├── styles.css
    ├── logo/app-icon.png, logo/logo.svg
    └── package.json, vite.config.js   (only devDependency: vite ^5.2.0)
```

Note: while I worked, other untracked files appeared in the working tree (`site/`, `REWORK_LOG.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/`). I did not create them, and they are not part of this audit.

---

## 2. What works and what is broken

### 2.1 CLI (`cli-client/`)

| Check | Result |
|---|---|
| `ast.parse(main.py)`, `ast.parse(auth.py)` | OK |
| Import under Python 3.11 / 3.12 / 3.13 | OK |
| Import under Python 3.9 | **FAIL**: `TypeError` at `main.py:63` (`-> str \| None`). Also `main.py:129` and `main.py:670` |
| Start in a pty (120×40) | OK: splash screen "Welcome to Terminal Academy", then a 3-pane UI |
| `help`, `status`, `clear` | OK (`help` lists only these 4 commands, `main.py:1147`) |
| Any real shell command (`ls -la`, `pwd`) | **Not executed.** Prints `Command 'ls -la' not found. Try 'help'.` (`main.py:1181`). No `subprocess` exists anywhere |
| Typing `1` (the boot text says "Type a module number", `main.py:109`) | **Broken promise**: `Command '1' not found` |
| Paste detection (3 keys within 4 ms) | Works. A pasted string triggers "Paste detected!" (pty test) |
| Resize the terminal | **CRASH**: `main.py:1728` `w_work, w_ank, h_panes = rebuild_windows(h, w)`, but `rebuild_windows` returns 5 values (`main.py:1522`). Reproduced with SIGWINCH |
| Terminal smaller than 90×24 | Shows "PLEASE RESIZE"; you can only quit with `q` (`main.py:1530-1548`) |
| Exit while the SOLO gate is armed | **Broken**: `exit` is scored as an "explanation" (`main.py:1032-1077` runs before the exit check). Tested: `rm -rf /tmp/x` then `exit` → "SOLO L3 FAIL (attempt 1/3)". The user must fail 3 times or press Ctrl+C |
| Cheat filter while the gate is armed | Skipped. `bypass_gate` is treated as an explanation (tested) |
| SOLO gate quality | **Easy to game**: plain substring keyword counting (`main.py:705`). `it uses private public key ed25519 entropy` passed (4/3 markers). The keyword `key` also matches words like "keyboard" |
| Module progression | Only module 1 has logic (`main.py:68-89`). Modules 2–5 can never be completed |
| Module 1 flow | Works only after you pick the module in the menu. `ssh-keygen` (gated) → `ssh-copy-id` → COMPLETED. Nothing really happens on disk |
| `sudo ...` commands | Always caught by the fake "eBPF" masker (`main.py:777`). They are never gated or explained |
| Login | Disabled. `run_login_gate` is commented out (`main.py:1481`); the session is hardcoded to `beta_tester` (`main.py:1482`) |
| Menu "Tariffs & Pricing" | Shows fake prices ($15/mo) and "BETA ACCESS GRANTED" (`main.py:869-876`) |

### 2.2 Desktop (`terminal-academy-desktop/`)

| Check | Result |
|---|---|
| `npm ci` | OK (38 top-level packages) |
| `npm run build` (`tsc -b && vite build`) | OK. One 680 kB JS chunk (warning: chunk > 500 kB) |
| `oxlint` | 7 warnings: missing hook dependencies (`App.tsx:191,386,393,1000,1540`) and control characters in regexes (`App.tsx:290-291`) |
| `cargo check` | Could not run here (missing GTK/WebKit libs). Not verified |
| Sandbox | Works only on the author's Mac. Uses `/Users/ank/.ssh/id_ed25519` and `root@89.22.239.107` (`lib.rs:24-31, 145-167`). For everyone else `has_docker` is false, so it spawns **the local zsh/bash/sh** (`lib.rs:177-186`): no sandbox at all. The UI only shows a red "SANDBOX OFFLINE (HOST SYSTEM ACTIVE!)" banner (`App.tsx:348-363`) |
| JWT "verification" | Fake. Decodes the payload without checking the signature and only tests `vpc_verified == true` (`lib.rs:96-111`). The literal token `dev_bypass` also passes (`lib.rs:121`). The default token in the UI is a hardcoded mock (`App.tsx:1772`) |
| System Monitoring widget | **Fake numbers**: CPU, RAM, disk, network etc. come from `Math.random()` (`App.tsx:1889-1927`). Only `dockerStatus` is real |
| Gemini API key UI | Removed. The README still says to use "UI Settings" (`desktop README.md:33`), but `showSettings`/`saveKey` are dead (`App.tsx:730`). The key can only come from `localStorage` or `public/config.json` |
| Russian translation | Loaded (`App.tsx:2004-2015`) but never shown, because `lang` is hardcoded to `'en'` (`App.tsx:1745`) |
| Skill tree ↔ curriculum | **Mismatched IDs.** `curriculum_graph.json` nodes `git-*`, `log-*`, `hard-*` use `nodeId` 21–32, but `curriculum_hosting.md` has only 20 nodes, so the panel shows "Loading incidents details..." forever (`App.tsx:1189-1233`). Labels do not match content either: `net-1` "SSH & Port Forwarding" → network Node 1 is "Network Interfaces"; `linux-2` "CLI Scripting" → Linux Node 2 is "File Management"; `devops-3` "gVisor & eBPF" → DevOps Node 3 is "Docker Volumes" |
| `parseSyllabus` on network/devops files | Those files use a different markdown format (`**Focus**`, `**Name**: desc`, `**Boss Fight: X**:`). As a result, descriptions are empty and titles contain `**` (`App.tsx:96-127`) |
| Command capture for Ank | Fragile. Reads the current line and splits on `$`, `#` or `>` (`App.tsx:196-201`), so `echo a > b` is captured as `b` |
| Update checker | Calls `api.github.com/repos/888ank888/...` (`App.tsx:1784`), but the git remote is `ank8dev/terminal-academy-by-ank`. Same old owner in `web-landing/index.html:53,188-208` |

### 2.3 Infrastructure

- `docker-compose.yaml:17` mounts `./infra/gvisor_events.sock`. `infra/` was deleted (commit `a0c5bd3`) and is gitignored. `runtime: runsc` needs gVisor on the host. Nothing in the code calls the Presidio container (`docker-compose.yaml:35-41`). `version: '3.8'` is obsolete in Compose v2.
- `Dockerfile.sandbox:1`: `alpine:3.18` has reached end of life. It installs `sudo` and `openssh-server`, but `student` is not in sudoers and sshd is never started. Also, `/home/student` is mounted `noexec` (`docker-compose.yaml:21`), so students could not run scripts they write. That is bad for a scripting course.
- `release.yml` builds only the desktop app. `pages.yml` deploys only on `main` and uses `npm install`, not `npm ci`.
- `web-landing` builds OK. `npm audit` reports 3 high/moderate issues (vite 5 / esbuild / nanoid / postcss). They affect the dev server only.

### 2.4 Misleading statements

| Where | Claim | Reality |
|---|---|---|
| `README.md:65` | "use the helper script `./start.sh`" | `start.sh` is gitignored (`.gitignore:26`) and was deleted in `a0c5bd3` |
| `README.md:43-46` | Repository layout | Does not mention `cli-client/`, `docker-compose.yaml` |
| `README.md` | "Zero-Risk Sandbox Virtualization … no threat to the host OS" | Falls back to the host shell (`lib.rs:177-186`) |
| `README.md` | "Windows MSI ~3 MB" etc. | Not verifiable; the new plan targets macOS/Linux only |
| `web-landing/index.html:67` | "zero-dependency, pure-terminal learning platform" | The button downloads a Tauri desktop app (`index.html:70-72`) |
| `web-landing/index.html:88-92` | "0 External Dependencies", "5 Mission Modules" | Desktop needs Docker + server + Gemini; desktop has 80 curriculum nodes |
| `web-landing/index.html:149` | "Ank tracks your live terminal state … validates your solutions, and rewards you" | No validation or reward logic exists |
| `web-landing/index.html:159` | "20-Node Skill Tree" | Graph has 33 nodes |
| `main.py:1150` | `ISOLATION: ACTIVE (gVisor)` | No container is used by the CLI |
| `main.py:878-884` | "Sandbox: gVisor", "SOLO Taxonomy semantic grader" | Neither exists; the grader is substring counting |
| `main.py:1107-1111` | "eBPF uprobe attached to libc.so.6 … Presidio sidecar" | Pure string replacement (`main.py:776-790`) |
| `main.py:255-260, 291-298` | "Temperature T=0.1 enforced" | No model is used; this is decoration |
| `desktop README.md:58-60` | `npm run build` builds installers | It builds only the web frontend |
| `web-landing/index.html:188-208` | Asset names `terminal-academy_<ver>_universal.dmg` | Tauri names files after `productName` "Terminal Academy" (`tauri.conf.json:3`); could not verify (API blocked) |

---

## 3. Dead code, duplicates, unused files

### 3.1 CLI (`cli-client/main.py`, `auth.py`)

| Location | Problem |
|---|---|
| `main.py:5` | `verify_session`, `AuthenticationError` imported but unused (ruff F401) |
| `auth.py` (whole file) | Never called. Fake prefixes `pro-`/`starter-` (`auth.py:11-14`), endpoint `https://api.terminal.academy/v1/auth` (`auth.py:5`) |
| `main.py:1255-1404` | `run_login_gate()`: unused (call commented out at `main.py:1481`) |
| `main.py:736-761`, `850` | `SubscriptionTierMatrix`: fake pricing; only used to print fake CPU/RAM |
| `main.py:33`, `1485` | `user_tier` used only for fake tier display |
| `main.py:767-781`, `848` | `EBPFSecurityInterceptor`: fake |
| `main.py:787-790`, `849` | `PresidioSidecarScrubber`: fake (prepends a string) |
| `main.py:1129-1141` | "Layer 4" is an exact copy of "Layer 3" (`main.py:1100-1112`) and can never trigger |
| `main.py:135-139` vs `264-267` | **Duplicate cheat-pattern lists** (`SocraticMentor.intercept_cheat` and `RuleEnforcementEngine.evaluate_input`). The second adds only `skip_logic`. Layer 2 is reachable only for `skip_logic` |
| `main.py:126-127` | `SocraticMentor.name`, `.tone` never read |
| `main.py:259-260` | `RuleEnforcementEngine.history_buffer` (grows forever, never read), `deterministic_temperature` unused |
| `main.py:153-172` | `TerminalAnimationEngine` always shows "STATUS: PROCESSING" (decoration) |
| `main.py:702` | `rubric.get("min_hits")`: no rubric defines `min_hits` |
| `main.py:1560` | `ank_border_color` assigned, then overwritten at `main.py:1594` before use |
| `main.py:82` | Sets module 2 to `READY`, but it is already `READY` (`main.py:46`) |
| `main.py:105` | "BETA: ALL UNLOCKED"; the `LOCKED` badge (`main.py:103`) is never used |
| `main.py:949-952` | Docstring mentions `mentor_visible_lines`, which no longer exists |
| `main.py:1222-1226` | Main menu list duplicated from `main.py:28-32` |
| Many "FIX:" comments (`main.py:133, 734, 949, 1500, 1533, 1691, 1718, 1745`) | Old change-log notes; remove them |

### 3.2 Desktop (`App.tsx`, `lib.rs`)

| Location | Problem |
|---|---|
| `App.tsx:419-426, 469-476, 616-623, 683-690` | **Same Gemini system prompt copied 4 times** |
| `App.tsx:428-439, 478-489, 545-552, 625-636, 692-703` | **Same `fetch` to Gemini copied 5 times** |
| `App.tsx:1889-1927` | `.then` and `.catch` branches build the same fake stats object twice |
| `App.tsx:507` vs `App.tsx:1979` vs `public/blacklist.json` | Three different "dangerous command" lists |
| `App.tsx:730-731` | `_unused` hack to silence `noUnusedLocals` (`activeCourse`, `activeNode`, `activeIncident`, `terminalBuffer`, `systemStats`, `showSettings`, `apiKey`, `saveKey` ...) |
| `App.tsx:1779-1780` | Same hack: `bootStage`, `setJwtToken`, `isVerifying` unused |
| `App.tsx:13-59` | `apiSettings`, `saveKey`, `askButton`, `incidentsTitle` strings never rendered |
| `App.tsx:1745`, `2004-2015` | `lang` fixed to `'en'`, so the Russian translation is dead |
| `App.tsx:2305-2306` | Empty `<AnimatePresence>` |
| `App.tsx:719-727` | `cleanMarkdown` removes every `#` and `*`, which breaks shell text like `#!/bin/bash` or `*.log` |
| `App.tsx:1062` | Grid background `rect` is 1080×650 inside a 2400×2000 canvas |
| `App.tsx:1767`, `2402` | `terminalBufferRef` collected but never used (ends in `_unused`) |
| `curriculum_graph.json` `"edges"` | Never read; the app uses `deps` |
| `lib.rs:24-31, 145-167, 259-268, 279-286, 296-314, 333-340` | Same SSH command builder copied 7 times |
| `lib.rs:55-94` | Hand-written base64 decoder (only used for the fake JWT check) |
| `index.html:8-27` | Yoti SDK script + mock with a hardcoded fake JWT; no code uses `window.Yoti` |

### 3.3 Unused assets and files

| File | Status |
|---|---|
| `src/assets/react.svg` (4 KB, one line) | Unused. Not empty: it shows as 0 lines in `wc -l` because it has no newline |
| `src/assets/vite.svg` | Unused |
| `src/assets/hero.png` | Unused |
| `public/icons.svg` | Unused (Vite template social icons) |
| `public/favicon.svg` | Used by `index.html:5`, but it is the default Vite logo, **not empty** and not project branding |
| `src-tauri/icons/android/**`, `icons/ios/**`, `Square*Logo.png`, `StoreLogo.png` | No mobile or Windows Store build exists |
| `public/translation_ru.json` | Tracked in git, but also listed in `terminal-academy-desktop/.gitignore:27`; never shown |
| `docker-compose.yaml`, `Dockerfile.sandbox` | Not used by the CLI; the desktop expects them on the remote server |

---

## 4. Dependencies

### 4.1 CLI
- Python stdlib only: `curses`, `time`, `sys`, `collections`, `urllib`, `json`. Good for the new plan.
- `curses` is not available on Windows without `windows-curses` (fine, since Windows is out of scope).
- Actual minimum Python is **3.10** (because of `X | None`). Add `from __future__ import annotations` or use `Optional[...]` to support 3.9.

### 4.2 Desktop npm (`terminal-academy-desktop/package.json`)

| Package | Where | Imported? | Comment |
|---|---|---|---|
| `react`, `react-dom` 19.2 | deps | yes | OK |
| `framer-motion` ^12.41 | deps | yes (`App.tsx:2`) | Now published as `motion`; 14.x exists |
| `@use-gesture/react` | deps | yes (`App.tsx:3`) | OK |
| `lucide-react` | deps | yes, **one icon** (`CheckSquare`, `App.tsx:4`) | Heavy for one icon |
| `xterm` ^5.3.0 | deps | yes (`App.tsx:5,7`) | **Deprecated** ("Move to @xterm/xterm") |
| `@xterm/addon-fit` ^0.11.0 | deps | yes (`App.tsx:6`) | Built for the new `@xterm/xterm`, mixed with old `xterm` 5 |
| `clsx` | deps | **no** | Unused |
| `@types/react-grid-layout` | deps | **no** | Types for a library that is not installed; also belongs in devDeps |
| `@types/react-resizable` | deps | **no** | Same |
| `@tauri-apps/api` | **devDeps** | yes (runtime, `App.tsx:8-9`) | Should be in `dependencies` (works only because Vite bundles it) |
| `@tauri-apps/cli`, `vite`, `typescript ~6.0`, `oxlint`, `@vitejs/plugin-react`, `@types/*` | devDeps | build tools | OK. `@types/node` is not needed by `src/` |

`npm outdated`: only minor updates, plus `framer-motion` 14 and `typescript` 7 majors. `npm audit` showed no blocking issues.

### 4.3 Desktop Rust (`Cargo.toml`)
`tauri 2.11`, `tauri-build 2.6`, `tauri-plugin-log 2`, `portable-pty 0.8`, `serde`, `serde_json`, `log`. Package metadata is still the template (`name = "app"`, `version = "0.1.0"`, `authors = ["you"]`, `Cargo.toml:2-6`). `serde` derive is not used.

### 4.4 Web landing
Only `vite ^5.2.0` (devDep). It is two majors behind (8.x) and `npm audit` flags its dev server. Google Fonts are loaded from the CDN (`index.html:14-16`).

---

## 5. Security and privacy

| # | Severity | Finding |
|---|---|---|
| 1 | **Critical** | Hardcoded root SSH to a private server: `root@89.22.239.107` with key `/Users/ank/.ssh/id_ed25519` (`lib.rs:26-29` and 6 more places; also `desktop README.md:32`). It reveals infrastructure, uses root, and only works on one laptop |
| 2 | **Critical** | Silent fallback to the **host shell** when the remote sandbox fails (`lib.rs:177-186`). A teenager can run `rm -rf ~` on their own machine. The blacklist is client-side substring matching (`App.tsx:228`) and is trivial to bypass (extra spaces, quotes, variables, typing the command in pieces) |
| 3 | High | Every command **and its output** goes to Google Gemini (`App.tsx:519-552`), plus the full chat history every time. Output can contain file contents, usernames and paths. A privacy problem for minors (COPPA/GDPR-K), and there is no consent screen |
| 4 | High | The Gemini API key is sent in the URL query string (`?key=...`, `App.tsx:428,478,545,625,692`) and stored in `localStorage` (`App.tsx:374,588`) |
| 5 | High | `public/config.json` with `default_api_key` (`App.tsx:2018-2030`, `desktop README.md:34-40`) is inside the Vite `public/` folder. If it exists at build time, it is **copied into `dist/` and shipped inside the installer**. Gitignored ≠ secret |
| 6 | Medium | Fake auth: unsigned JWT accepted (`lib.rs:96-111`), `dev_bypass` backdoor (`lib.rs:121`), mock token hardcoded (`App.tsx:1772`, `index.html:19`). `auth.py:11-14` gives a "pro" tier to any token that starts with `pro-` |
| 7 | Medium | `auth.py:5` would POST user tokens to `api.terminal.academy` (domain status unknown) |
| 8 | Medium | Remote `docker run` runs as root with a 2-hour `sleep` and a name based on a counter (`lib.rs:151-153`). Two users can race for the same index; there is no per-user isolation |
| 9 | Medium | `tauri.conf.json:24` `"csp": null` (CSP disabled); `index.html:8` loads a third-party script (`static.yoti.com`) into the privileged webview |
| 10 | Low | Update check and landing page call `api.github.com` on every start (`App.tsx:1784`, `web-landing/index.html:196`) and point to the old owner `888ank888` |
| 11 | Low | Keystroke telemetry (WPM, paste count) is kept in memory only (`main.py:178-246`); nothing is sent. Fine, but explain it if kept |

The new CLI should have **no network calls by default**, never call a shell with student-provided strings through `shell=True` without a sandbox directory, and keep all exercise files inside a dedicated folder (for example `~/.terminal-academy/sandbox/`).

---

## 6. Feature inventory

| Feature | CLI | Desktop | Worth keeping in new CLI? |
|---|---|---|---|
| Real shell where students type real commands | no (fake shell) | yes (PTY via `portable-pty`, `lib.rs:114-219`) | **yes**: this is the core of hands-on lessons. Use the student's own shell inside a safe practice folder |
| Remote Docker sandbox over SSH | no | yes (`lib.rs:23-53, 136-167`) | **no**: needs a server, root, one laptop |
| `reset` / `reset-sandbox` command | no | yes (`App.tsx:238-248`, `lib.rs:292-317`) | **yes, as an idea**: "reset this lesson" that recreates the exercise folder |
| docker-compose gVisor sandbox + Presidio | no | indirectly (remote) | **no** |
| Curriculum engine (5 modules, state machine) | yes (`main.py:39-110`) | no | **maybe**: keep the idea of steps with checks; rewrite with real checks |
| Module topics (SSH, local AI, Raspberry Pi, OSINT, iptables) | yes (`main.py:44-50, 891-940`) | no | **no**: too advanced or needs extra hardware/root |
| SOLO "explain before you run" gate | yes (`main.py:285-729`) | no | **maybe**: good teaching idea, but make it a short multiple-choice or free-text reflection, not a blocker. The gate questions are too deep for teens |
| Cheat-word filter (`bypass_gate` ...) | yes, twice (`main.py:129-147, 252-279`) | no | **no** |
| Keystroke paste detector + WPM | yes (`main.py:178-246`) | paste block (`App.tsx:187-216`) | **no / maybe**: blocking paste frustrates learners. Maybe a gentle hint only |
| Fake eBPF / Presidio masking | yes (`main.py:767-790`) | no | **no** |
| Pricing tiers / tariffs menu | yes (`main.py:736-761, 869-876`) | no | **no** |
| Login gate / token auth | yes, disabled (`main.py:1255-1404`, `auth.py`) | fake JWT (`lib.rs:96-121`) | **no**: use a local progress file instead |
| Splash screen / ASCII logo | yes (`main.py:1406-1437`) | no | **yes**: cheap and fun |
| 3-pane curses UI (work / mentor / HUD) | yes (`main.py:1474-1787`) | n/a | **maybe**: a full-screen UI hides the real terminal. A simple line-based CLI (print lesson → student runs commands in their own shell → `ta check`) fits hands-on learning better |
| Typing-stream mentor text | yes (`main.py:796-837`) | no | **maybe**: nice effect; must be skippable |
| Menus (Tab focus, arrows) | yes (`main.py:1194-1246, 1732-1787`) | no | **maybe**: a simple numbered menu is enough |
| `help` / `status` / `clear` / `exit` | yes (`main.py:1146-1178`) | no | **yes**: `help`, `status` (show real progress), `exit` |
| Mentor "Ank" persona (sarcastic) | scripted text | Gemini LLM (`App.tsx:370-717`) | **maybe**: keep the character and voice for hints, but make it friendlier for teens. Offline, pre-written hints only |
| AI mentor via Gemini | no | yes | **no** (by default): privacy, API key, network. Maybe a later opt-in |
| "Explain this command" (Grimoire) | no | yes (`App.tsx:834-893`) | **yes, offline**: a local `explain <cmd>` with short pre-written notes for the ~40 commands taught |
| Command blacklist | no | yes (`public/blacklist.json`, `App.tsx:228`) | **maybe**: only as a warning list ("this command is dangerous"), not as security |
| Destructive-command warning | gate categories (`main.py:318-339`) | `App.tsx:507-514` | **yes**: warn before `rm -rf`, `dd`, `mkfs`, `chmod -R` |
| Skill tree (draggable SVG canvas) | no | yes (`App.tsx:1009-1245`, `curriculum_graph.json`) | **maybe**: an ASCII skill map / lesson list with locked/unlocked state |
| Curriculum markdown parser | no | yes (`App.tsx:76-143`) | **maybe**: a new, simple lesson format (one file per lesson) is better |
| Incident checklist (Planner) | no | yes, static (`App.tsx:1428-1484`) | **yes, as an idea**: each lesson = list of tasks with automatic checks |
| System monitoring widget | fake HUD (`main.py:1631-1645`) | fake random numbers (`App.tsx:895-976`) | **no** |
| 4-screen layout, drag/zoom, particles, HUD | no | yes (`App.tsx:1486-1737, 2039-2207`) | **no** |
| Russian translation | no | yes, unused (`translation_ru.json`) | **maybe**: support i18n later via a strings file; keep English first |
| Auto-update check (GitHub releases) | no | yes (`App.tsx:1782-1815`) | **maybe**: an optional `--check-update`, never automatic |
| Progress saving | no (in memory) | no | **yes (new)**: JSON file in `~/.terminal-academy/progress.json` |

---

## 7. Content worth reusing

**Best source: `curriculum_linux.md` Nodes 1–10.** These are scenario-based and fit a local, no-root practice folder. Examples that can become real exercises with automatic checks:

- Node 1 (Navigation): "Hidden Treasures" (find `.secrets`), "Space Invaders" (directory with spaces), "The Void" (directory named `-`), "Wildcard Chaos", "Tree Climber" (deep folders), "The Invisible Man" (odd file name). All can be generated in a practice folder and checked with Python `os`/`pathlib`.
- Node 2 (Files & archives): tar extract, copy without `.log` files, find and truncate a big file, combine split files, broken symlinks (in the practice folder, not `/etc`).
- Node 3 (Text processing): `grep` errors from a log, `awk` sum of a CSV column, `sort -n`, `uniq`, `head`/`tail` line ranges, `tr` for DOS line endings, `column`. These are great for teens and easy to check (compare output).
- Node 5 (Basic permissions): `chmod` on own files (no root needed).
- Node 7–8 (Bash scripting): loops, conditions, arguments. Needs a practice folder **without** `noexec`.
- Node 9–10 (Processes, jobs): `ps`, `kill`, `&`, `fg`/`bg`, `jobs`; `crontab` only as an explanation.
- Skip or postpone nodes that need root or a server: 4 (users), 6 (ACLs), 11–20 (packages, systemd, LVM, network config, firewall).

**`curriculum_network.md`:** only Node 2 (ping/traceroute) and Node 4 (DNS with `dig`/`/etc/hosts`) as read-only exploration. Nodes 8, 9, 14, 15, 18 and 20 cover offensive-security and attack topics. **Do not reuse them for a teen course.**

**`curriculum_devops.md`, `curriculum_hosting.md`:** too advanced and need Docker or root. Possible later "bonus" ideas: Hosting Node 7 (run a Minecraft server). It is very motivating for teens but needs Java and lots of RAM, so treat it as optional.

**`main.py` SOLO rubrics (`main.py:348-658`):** the `gate_question` texts are good "why does this work?" prompts for advanced learners, but they must be simplified for teens (for example: "Why must your private key file be readable only by you?"). The `permissions`, `destructive_fs` and `scheduling` rubrics are the most reusable.

**`blacklist.json`:** useful as a list of "dangerous command" examples for a safety lesson. Not useful as a security control.

**Mentor voice:** the landing demo dialog (`web-landing/script.js:4-19`) shows the intended tone well: short and funny, with a question. Reuse this style for offline hints, but make it less condescending ("kid", "grandma") for young learners.

**`curriculum_graph.json`:** the dependency idea (lesson unlocks lesson) is reusable; the coordinates and IDs are not (they do not match the markdown, see §2.2).

---

## 8. Prioritized recommendations

### Stage 5: cleanup (wave 2)

1. **Remove secrets and infrastructure details first.** Delete `terminal-academy-desktop/` (this removes the SSH IP, key path, mock JWT, Yoti mock and config.json logic). Also remove the IP from `desktop README.md`. Consider rotating/removing the author's key from that server, because the IP is in git history.
2. Delete `.github/workflows/release.yml` (desktop builds). Update `pages.yml` only if the landing page stays.
3. Delete `docker-compose.yaml` and `cli-client/Dockerfile.sandbox` (unused, broken socket mount, EOL base image). Keep them in git history only.
4. Delete `cli-client/auth.py` and the import at `main.py:5`.
5. In `main.py`, remove the fake/dead parts: `SubscriptionTierMatrix`, `EBPFSecurityInterceptor`, `PresidioSidecarScrubber`, `RuleEnforcementEngine` (duplicate list), `run_login_gate`, `pricing_text`, `docs_text`, `user_tier`, "Tariffs & Pricing" menu, the duplicate Layer 4 block, fake `status` lines, the "T=0.1" and "FIX:" comments.
6. Fix the two real bugs if any old code stays for a while: resize crash (`main.py:1728`) and the 3.9 incompatibility (`main.py:63,129,670`).
7. Rewrite `README.md`: one command to start, real requirements (Python 3.9+, macOS/Linux), no `start.sh`, no sandbox/AI claims. Fix the repo owner in links (`888ank888` → `ank8dev`).
8. Landing page: replace the "Download Desktop App" button and false stats (`index.html:67-92, 141-160`) with the CLI install command. Close the missing `</section>` after the features grid (`index.html:174-175`). Update vite or drop the npm build (the page is plain HTML/JS and can be served as static files).
9. Move reusable content out of the desktop folder **before** deleting it: `curriculum_linux.md` (and optionally `blacklist.json` as safety-lesson material) → for example `content/reference/`.

### Stage 6: CLI migration

1. **Architecture:** one package (for example `terminal_academy/`) with a `__main__.py`, so it runs with `python3 -m terminal_academy` or a tiny `ta` launcher script. Stdlib only. Add `from __future__ import annotations` everywhere and test on 3.9 (CI matrix 3.9 + latest on ubuntu and macos).
2. **Lesson model:** one file per lesson (JSON, or Python dicts, to avoid a YAML dependency) with: title, story text, tasks, a `setup()` that creates files in `~/.terminal-academy/lessons/<id>/`, and a `check()` that inspects the folder or the output. The student works **in their own real terminal**. The CLI only prints the task, sets up files, and verifies (`ta start 1`, `ta check`, `ta hint`, `ta reset`).
3. **Safety:** never run student commands through the tool; never touch files outside the practice folder; warn about dangerous commands in the lesson text. No network by default.
4. **First lesson set (from `curriculum_linux.md` Nodes 1–3, 5, 7, 9):** about 15–20 short lessons: `pwd`/`ls`/`cd`, hidden files, quotes and spaces, `mkdir`/`cp`/`mv`/`rm`, wildcards, `cat`/`less`/`head`/`tail`, `grep`, pipes and `>`/`>>`, `sort`/`uniq`/`wc`, `chmod`, first bash script, `ps`/`kill`/jobs, `tar`.
5. **Keep from the old CLI:** splash logo, Ank's voice in pre-written hints, the "explain why" idea as an optional reflection question (no keyword-score gate), simple color output (ANSI codes; curses is not needed).
6. **Progress:** save to `~/.terminal-academy/progress.json`; `ta status` shows done/next lessons as a small ASCII skill map (the idea from the desktop skill tree).
7. **Optional later:** offline `explain <command>` notes, i18n strings file (RU translation as a second language), opt-in AI hints.
