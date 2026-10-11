# Terminal Academy — website

The landing page and brand guide for Terminal Academy (`t//a`). Plain static
files: no build step, no frameworks, no JavaScript. Google Fonts (Space Grotesk,
Inter, JetBrains Mono) are loaded when available; every font has a system
fallback, so the pages also work offline.

## Structure

| Path | What it is |
| ---- | ---------- |
| `index.html`, `styles.css` | Landing page: hero with install snippet and a lesson mock, the course map (15 lessons in 5 levels), how it works, who it's for, safe by design, open source, footer with the disclaimer. |
| `brand/index.html` | One-page brand guide: logo variants, sizes, clear space, colors (hex + ANSI 256), typography, voice and tone, and a mock of the CLI welcome screen. It reuses `../styles.css`. |
| `brand/logo-mark.svg` | Primary mark (`t//a` on an Ink rounded square). Letters are drawn as shapes, no fonts. Use at 48px and up. |
| `brand/logo-mark-small.svg` | Small mark (`//` + cursor) for 32px and below. |
| `brand/logo-wordmark.svg`, `brand/logo-wordmark-dark.svg` | Mark + "Terminal Academy" (text converted to paths) for light and dark backgrounds. |
| `favicon.svg`, `favicon.ico` | Favicons (small mark; the ICO holds 16, 32 and 48 px PNGs). |
| `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` | App icons (primary mark). |
| `site.webmanifest` | Web app manifest (name, short name `t//a`, colors, icons). |
| `og-image.png` | 1200×630 social preview image. |

Brand rules (colors, words to use and avoid, logo rules) are on the brand guide page.
The PNG/ICO icons are rendered from the SVGs; if you change a logo SVG, re-render them.

## Preview

```sh
python3 -m http.server -d site
# then open http://localhost:8000 (brand guide: http://localhost:8000/brand/)
```

Opening `site/index.html` directly in a browser works too.
