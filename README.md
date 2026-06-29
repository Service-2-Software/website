# Service 2 Software — Website

Marketing site for Service 2 Software (S2S): we turn proven military leaders into
high-performing sales professionals and place them with companies that need
ramp-ready talent.

This is a static, multi-page site (no build step). Open any `.html` file or serve
the folder with any static server.

```bash
python3 -m http.server 8080   # then visit http://localhost:8080
```

## Structure

```
index.html              Home
military.html           For Military (program, apply form)
companies.html          For Companies (ROI calculator, booking form)
about.html              About (story, founder, team, principles, impact)
blog.html               Blog / Resources index
skillbridge-guide.html  Example article (template for blog posts)
assets/
  css/styles.css        Single brand stylesheet (design tokens + components)
  js/main.js            Shared nav + mega menu + footer + ROI calc + forms
  fonts/                Drop the real TT Lakes Condensed Bold file here
  img/                  Local imagery
```

The nav and footer are injected by `assets/js/main.js` into `#site-nav` and
`#site-footer` on every page, so there is a single source of truth for site chrome.

## Brand system (encoded in `styles.css`)

- **Type:** TT Lakes Condensed Bold = wordmark · Oswald = display + labels · Barlow = body.
  TT Lakes falls back to Oswald until the real font file is added to `assets/fonts/`.
- **Color:** strict **black-first** alternating sections (`.sec.k` / `.sec.w`); disciplined
  lime accent (`--lime`) sprinkled into every section via eyebrow lines, checkmarks,
  hover edges, focus rings, and the primary CTA.
- **Shape:** parallelogram CTAs (`.btn`), thin straight eyebrow lines (lime on black,
  black on white), hollow display words (`.hollow`).
- **Mega menu:** custom hand-drawn glyphs in skewed parallelogram tiles that fill lime
  on hover (intentionally not a copy of any other site).

### Canonical stats (use these everywhere)

`96%` employment · `$330K` training contributed (2025) · `8x` average partner ROI ·
`70%` fellowship-to-hire · `3.5x` meeting yield vs. industry · `65%` cost savings ·
`0` added headcount burden during ramp · `600+` transitions supported.

## Open TODOs (placeholders in code)

- `S2S Core` portal URL (login links currently show a "coming soon" notice).
- ActiveCampaign form IDs for the military + companies lead forms (`data-lead` in
  `main.js`). AC then handles the follow-up email + Salesforce + Slack.
- Real ROI program cost (`ROI.programCost` in `main.js`, currently a placeholder).
- Real TT Lakes Condensed Bold font file in `assets/fonts/`.
- Real favicon (inline SVG placeholder in each page `<head>`).
- Blog article copy (drop into article pages modeled on `skillbridge-guide.html`).
- `testimonial.to` Wall of Love embed id is wired on the home page.

## Branch plan

`cursor/s2s-website-foundation-adc8` establishes the repository, shared chrome, and
all pages. From here, per-page (and per-section) branches can be cut off `main` for
isolated refinement, e.g. `cursor/home-hero-adc8`, `cursor/companies-roi-adc8`.
