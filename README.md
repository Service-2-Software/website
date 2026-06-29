# Service 2 Software — Website

Marketing site for **Service 2 Software (S2S)** — a DoD SkillBridge approved
501(c)(3) that turns transitioning service members into high-performing software
sellers and places them with hiring companies. Brand line: **"Hire With Purpose."**

This repo is the production source, ported from the design Claude built in the
build chat and restructured from a single-page app into a real multi-page site
(better for SEO and for the per-page / per-section workflow below).

## Structure

```
index.html             Home
for-military.html      For Military
for-companies.html     For Companies (includes the ROI calculator)
about.html             About
blog.html              Blog index
blog/                  Individual article pages
partials/
  nav.html             Shared nav + 4 mega menus (single source of truth)
  footer.html          Shared footer
assets/
  css/
    styles.css         Design tokens + components (the brand system)
    nav.css            Nav + mega menu
    home.css           Home-page layout
  js/
    include.js         Injects partials, fires "partials:loaded"
    nav.js             Mega menu + mobile nav
    roi-calculator.js  ROI calculator logic
    forms.js           Lead forms -> Calendly thank-you step
  fonts/               TT Lakes Condensed Bold goes here (see fonts/README.md)
  favicon.svg          Black tile, lime S²
```

## Brand system (encoded in `assets/css/styles.css`)

- **Type:** TT Lakes Condensed Bold (wordmark) · Oswald (headlines, labels,
  buttons, nav) · Barlow (body copy).
- **Color:** strict black ↔ white section alternation (black first). Lime
  (`--c-lime: #b4f000`) is a disciplined accent reserved for CTAs + small
  highlights (eyebrow rules on black, checkmarks, hover edges, focus rings).
- **CTAs:** parallelogram clip-path, 15px Oswald. Primary = lime; ghost = thin
  (1.2px) outline that fills lime on hover.
- **Eyebrows:** thin straight rule + label (lime on black, black on white).
- **Hollow text:** 1.2px stroke (white on dark, dark on white).
- **Mega menu:** custom hand-drawn SVG glyphs in parallelogram icon tiles.

## Running locally

Static site — serve the folder over HTTP (partials load via `fetch`, so
`file://` won't work):

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Branch workflow

- `cursor/site-foundation-*` — shared system + home (this PR).
- `cursor/page-<name>-*` — one branch per page (each adds its own file).
- `cursor/<page>-section-<name>-*` — per-section refinements within a page.

## Open integration TODOs (search the code for `data-todo` / `TODO`)

- Patrick's intro-call Calendly URL (`assets/js/forms.js`).
- ActiveCampaign form IDs (Military Application / Partner Inquiry).
- Real S2S Core portal URL (currently `#`).
- Real ROI program cost (`PROGRAM_COST` in `roi-calculator.js`).
- logo.dev publishable token (ticker `?token=`).
- TT Lakes Condensed Bold font file (`assets/fonts/`).
- Confirm RateMySkillBridge page is live.
