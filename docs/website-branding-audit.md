# Service 2 Software website branding audit

## Current repository state

- The repository currently contains `README.md` only.
- The latest single-file website HTML referenced in the prior Claude chat is not checked into this repository yet.
- Before page or section implementation branches can be created, import the current `index.html` and any supporting assets into this repository.

## Branding decisions to preserve sitewide

- Wordmark: use `TT Lakes Condensed Bold` for `SERVICE 2 SOFTWARE` lockups.
- Display headlines: use `Oswald Bold`.
- Body copy: use `Barlow` for readability, especially paragraphs on black backgrounds.
- CTAs: use larger text and parallelogram button shapes sitewide.
- Lime green: use as an accent, not the dominant color.
- Hollow text: use thin white outlines on dark backgrounds; avoid thick outline strokes.
- Section rhythm: start page sections on black and alternate black/white.
- Eyebrow marks: use thin straight lines, lime on black sections and black on white sections.
- Footer: remove the "HIRE WITH PURPOSE." tagline from the footer sitewide.
- Footer readability: increase social icons, footer link text, and grey text contrast on black.
- Mega menu: keep custom parallelogram icon tiles, not number-only items and not a direct 7 Eagle copy.
- Copy style: remove AI-looking em dashes from prose and rewrite with proper punctuation.

## Confirmed content decisions

- Employment rate: `96%`.
- Training contribution: `$330K` in 2025.
- ROI: standardize on `8x`.
- Ramp language: use `0 added headcount burden during ramp`, not `0 ramp time`.
- RateMySkillBridge URL: `https://ratemyskb.com/company/service-2-software`.
- Company Calendly URL: `https://calendly.com/davidhester/s2s-hiring`.
- Testimonial embed:
  `<iframe id="testimonialto-0f9fe1c1-b3b4-4f10-9ce5-8b3b07b8994a" src="https://embed-v2.testimonial.to/w/service-2-software?id=0f9fe1c1-b3b4-4f10-9ce5-8b3b07b8994a" frameborder="0" scrolling="no" width="100%" height="800px"></iframe>`

## Open items before production wiring

- Patrick's Calendly URL for military intro calls.
- ActiveCampaign form IDs for military applications and partner inquiries.
- Salesforce routing details for recruit vs. partner leads.
- Real annual partnership/program cost for the ROI calculator assumptions.
- S2S Core portal URL.
- Final favicon asset.
- `logo.dev` token/domain choices for partner logos.

## Proposed branch workflow

Use one integration branch for importing the current site, then split page and section work from that baseline.

### Initial import

- `cursor/import-current-site-8516`: add the latest `index.html`, ROI calculator source, fonts, images, and any scripts/styles.

### Page branches

- `cursor/home-page-branding-8516`
- `cursor/military-page-branding-8516`
- `cursor/companies-page-branding-8516`
- `cursor/about-page-branding-8516`
- `cursor/resources-blog-branding-8516`
- `cursor/footer-nav-branding-8516`

### Section branches

Create section branches only after the imported HTML is modular enough to avoid painful merge conflicts. Suggested names:

- `cursor/home-hero-8516`
- `cursor/home-results-8516`
- `cursor/home-audience-cards-8516`
- `cursor/home-newsletter-8516`
- `cursor/military-hero-8516`
- `cursor/military-program-8516`
- `cursor/military-application-form-8516`
- `cursor/companies-hero-8516`
- `cursor/companies-partner-results-8516`
- `cursor/companies-roi-calculator-8516`
- `cursor/companies-booking-form-8516`
- `cursor/about-beliefs-8516`
- `cursor/about-team-8516`
- `cursor/resources-blog-index-8516`
- `cursor/resources-blog-articles-8516`

## First audit pass once HTML is imported

- Verify the footer appears once per page/view and uses shared markup.
- Verify section color alternation on every page.
- Verify CTA classes are shared and all CTA boxes are parallelograms.
- Verify grey text contrast and size on black and white sections.
- Verify hollow outline thickness sitewide.
- Verify ROI calculator placement under the Companies page.
- Verify copy has no em dashes in prose.
- Verify menu icons use the final custom icon treatment.
- Verify blog/article links are real or intentionally marked as placeholders.
