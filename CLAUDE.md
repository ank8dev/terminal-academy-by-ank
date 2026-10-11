# Terminal Academy (t//a)

Systems-first learning platform: a Tauri desktop app with a draggable skill-tree canvas, a Docker sandbox terminal, and an AI mentor ("Ank", Gemini API). Plus a marketing site on GitHub Pages.

## Layout

| Path | What it is |
|---|---|
| `terminal-academy-desktop/` | The product. React 19 + TS + Vite 8 frontend, Tauri v2 / Rust backend (`src-tauri/src/lib.rs`: `spawn_pty`, `write_pty`, `resize_pty`, `get_docker_status`, `destroy_sandbox`, `reset_sandbox`). Almost all UI lives in one file, `src/App.tsx` (~2.5k lines). |
| `web-landing/` | Marketing site. React 19 + TS + Vite 5, multi-page: `index.html` (variant hub) and `variant-1..5.html`. Deployed to GitHub Pages. |
| `cli-client/` | Python CLI prototype + `Dockerfile.sandbox` (sandbox image used by `docker-compose.yaml`). |
| `docker-compose.yaml` | Sandbox container (gVisor `runsc`, read-only, no caps) + Presidio PII sidecar. |

## Commands

```bash
# Landing (this is what CI builds)
cd web-landing && npm ci && npm run build   # tsc + vite build -> web-landing/dist
cd web-landing && npm run dev

# Desktop
cd terminal-academy-desktop && npm ci
npm run dev        # browser-only frontend
npm run desktop    # tauri dev (needs Rust toolchain)
npm run build      # tsc -b + vite build
npm run lint       # oxlint
```

There are no tests. `npm run build` (type-check + bundle) is the verification gate: run it in every package you touched before committing.

## How the landing reuses desktop code (read before touching either)

The landing variants import real desktop widgets, e.g. `import { TerminalWidget, ChatWidget } from '~/App'`. These are the `export`s in `terminal-academy-desktop/src/App.tsx`.

- `~` → `../terminal-academy-desktop/src`, `@` → `web-landing/src` (`vite.config.js` + `tsconfig.json`).
- `@tauri-apps/api/core` and `/event` are aliased to `web-landing/src/mockTauri.ts`, which fakes the PTY, sandbox and docker status in the browser. If desktop code starts calling a new Tauri command or event, add it to the mock, or the landing will reject with "Unknown mock tauri backend command".
- Desktop source compiled for the landing resolves npm packages from **`web-landing/node_modules`**. That is done by `resolve.dedupe` in `vite.config.js` and the `"*"` path in `tsconfig.json`. CI installs only the landing's deps, so do not undo this: a clean checkout would stop building and React would get bundled twice. Any package `App.tsx` imports must also be a dependency of `web-landing` and listed in `dedupe`.
- `web-landing/tsconfig.json` type-checks `../terminal-academy-desktop/src` with the landing's strict settings (`noUnusedLocals` etc.). A desktop change can therefore break the landing build. Build both.
- Note the version skew: the landing uses `lucide-react` 0.475 and the desktop uses 1.x. Icons used by `App.tsx` must exist in both.

## Data files

`blacklist.json`, `curriculum_*.md`, `curriculum_graph.json` and `translation_ru.json` are **duplicated** in `terminal-academy-desktop/public/` and `web-landing/public/` (currently identical). Edit both copies.

`config.json` (`{"default_api_key": ...}`, fetched at `/config.json`) is gitignored on purpose and is not in the repo. Never commit API keys. The app also accepts a user key stored in `localStorage` (`gemini_api_key`).

## Status / gotchas

- Branch `feature/experimental-landing-variants`: 5 competing landing designs (`src/variants/Variant1Classic` … `Variant5Bento`). The goal is to pick one or merge them into a single landing.
- `web-landing/script.js` and `web-landing/styles.css` are the old vanilla landing. No HTML references them any more, so they are dead code unless deliberately revived.
- The Vite config uses `base: './'` (relative assets for GitHub Pages). Keep it.
- `.github/workflows/pages.yml` deploys `web-landing/dist` on push to `main` (paths `web-landing/**`). The other workflow builds and releases desktop installers on `v*` tags. Bump the version in `terminal-academy-desktop/package.json` and `src-tauri/tauri.conf.json` together.
- The UI is bilingual EN/RU: the `t` dictionary in `App.tsx` plus `translation_ru.json`. Add strings in both languages.
- Gitignored local-only folders you may not see: `research_repos/` (reference clones), `chrome-profile/`, `infra/`, `.agents/`, `start.sh`.
