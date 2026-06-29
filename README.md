# Service 2 Software — Website

Static HTML/CSS/JS website for [service2software.com](https://service2software.com).

## Pages

| File | Description |
|------|-------------|
| `index.html` | Home page |
| `military.html` | For Military — SkillBridge program, how to apply |
| `companies.html` | For Companies — partner results, ROI calculator, booking |
| `about.html` | About S2S — story, team, mission, principles, FAQ |
| `blog/index.html` | Blog / Resources index |
| `blog/*.html` | 8 blog articles |

## Assets

```
assets/
├── css/
│   ├── global.css       — Design system (variables, reset, typography)
│   ├── components.css   — Buttons, cards, forms, grids
│   ├── nav.css          — Mega navigation
│   ├── footer.css       — Footer
│   ├── home.css         — Home page styles
│   └── pages.css        — Interior page styles
├── js/
│   ├── nav.js           — Navigation / mega menu logic
│   └── app.js           — ROI calculator, forms, animations
└── fonts/
    ├── TTLakesCondensedBold.ttf    ← Place font file here
    └── TTLakesCondensedBold.otf    ← Place font file here
```

## Setup

This is a static site — no build step required. Open any HTML file in a browser or serve with any static file server:

```bash
npx serve .
# or
python3 -m http.server 8080
```

## Required Actions Before Launch

1. **Font files** — Place `TTLakesCondensedBold.ttf` and `.otf` in `assets/fonts/`. The font is used for the `SERVICE2SOFTWARE` wordmark only.
2. **logo.dev token** — Replace `YOUR_LOGO_DEV_TOKEN` in `index.html` ticker logos with your real token from [logo.dev](https://logo.dev).
3. **Calendly URLs** — Military apply form thank-you: update Patrick's Calendly URL (currently points to davidhester/s2s-hiring as placeholder). Companies booking: already set to `calendly.com/davidhester/s2s-hiring`.
4. **S2S Core Login** — Replace `href="#"` on all "S2S Core Login" buttons with the real portal URL.
5. **ActiveCampaign forms** — Replace `data-action="#"` on `.s2s-form` elements with real AC form endpoints.
6. **RateMySkillBridge** — `https://ratemyskb.com/company/service-2-software` link is live when their listing goes active.
7. **Program cost** — Update `programCost` in `assets/js/app.js` ROI calculator with real partnership pricing.
8. **Images** — Add real hero background images and team photos; replace placeholder gradients.

## Brand

| Element | Font |
|---------|------|
| Wordmark ("SERVICE2SOFTWARE") | TT Lakes Condensed Bold |
| Headlines, labels, buttons | Oswald Bold / Oswald |
| Body text, descriptions | Barlow |

**Colors:** Lime `#CAFF50` · Black `#0A0A0A` · White `#FFFFFF`

**Buttons:** Parallelogram via `clip-path: polygon(14px 0%, 100% 0%, calc(100% - 14px) 100%, 0% 100%)`

## Branch Strategy

Each page has a dedicated branch for isolated review:

- `cursor/shared-assets-05ff` — CSS, JS, fonts
- `cursor/page-home-05ff` — Home page (index.html)
- `cursor/page-military-05ff` — Military page
- `cursor/page-companies-05ff` — Companies page
- `cursor/page-about-05ff` — About page
- `cursor/page-blog-05ff` — Blog system

Section-level branches for granular review:
- `cursor/section-home-hero-05ff`
- `cursor/section-home-stats-ticker-05ff`
- `cursor/section-home-audiences-results-05ff`
- `cursor/section-home-training-testimonials-05ff`
- `cursor/section-military-hero-05ff`
- `cursor/section-military-program-apply-05ff`
- `cursor/section-companies-hero-results-05ff`
- `cursor/section-companies-roi-calculator-05ff`
- `cursor/section-companies-how-it-works-booking-05ff`
- `cursor/section-about-hero-belief-05ff`
- `cursor/section-about-team-impact-principles-05ff`
- `cursor/section-blog-index-05ff`
- `cursor/section-blog-articles-05ff`
