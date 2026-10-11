# Terminal Academy — landing page variants

Three alternative landing page designs for Terminal Academy (`t//a`). Each one is a
static page made of plain `index.html` + `styles.css`: no build step, no frameworks,
no JavaScript. Google Fonts are loaded if available, and each page has a system-font
fallback, so it looks fine offline too.

| Folder | Style | Notes |
| ------ | ----- | ----- |
| `v1/`  | Retro terminal | Dark CRT look, green/amber phosphor, ASCII-art logo, CSS-only animated fake terminal session. |
| `v2/`  | Clean modern | Light, airy layout with rounded cards and colorful accents. Switches to dark mode automatically via `prefers-color-scheme`. |
| `v3/`  | Playful / game-like | Bold colors, quest map with lessons as levels, badges, a "player card" and chunky buttons. |

All three have the same sections: hero (headline, pitch, install snippet, GitHub
button), what you'll learn (the seven lesson levels), how it works (3 steps), who it's
for, open source / contribute, and footer. All links go to the GitHub repo or to anchors
on the same page. Animations are switched off when `prefers-reduced-motion` is set.

## Preview

Open `site/v1/index.html` (or `v2`, `v3`) directly in a browser, or serve a folder:

```sh
python3 -m http.server -d site/v1
# then open http://localhost:8000
```
