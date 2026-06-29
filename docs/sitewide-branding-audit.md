# Service 2 Software Website Branding Audit

This audit converts the prior Claude website decisions into repo-ready acceptance criteria. Use it when importing or reviewing the current HTML build.

## Current source status

- The repository currently does not contain the generated `index.html` from the Claude session.
- Before page or section refinement branches can be opened, import the latest Claude HTML into `src/index.html` or split it into the page structure selected for the build.
- Any branding issue found during review should be fixed once in the shared style layer when possible, not copied section by section.

## Sitewide brand decisions to preserve

### Typography

- `SERVICE 2 SOFTWARE` wordmark uses TT Lakes Condensed Bold.
- Display headlines use Oswald Bold.
- Labels, buttons, nav links, stat captions, and eyebrow text use Oswald.
- Body paragraphs, descriptions, quotes, and longer explanatory copy use Barlow.
- Avoid condensed fonts for paragraph copy.

### Color and contrast

- Lime green is an accent, not a dominant fill.
- Green should appear in controlled spots: CTA fills, focus states, checkmarks, selected model labels, important stat/result highlights, and subtle section accents.
- Black sections should use readable grey text. Any body copy on black should be light enough and large enough to scan comfortably.
- White sections should use darker grey for Oswald labels and captions. Avoid low-contrast light grey.
- Sections should follow a black-first alternating rhythm wherever possible.

### CTA treatment

- CTAs should use the parallelogram shape language sitewide.
- CTA font size should be large enough to feel intentional, not utility-sized.
- Military primary CTA language should standardize around `Apply Now`.
- Company primary CTA language should standardize around `Schedule a Call`.
- Outlined CTA variants should remain readable on both black and white backgrounds.

### Hollow text treatment

- Hollow outline text should be thin and crisp, not heavy.
- On black backgrounds, hollow text should use a bright white stroke.
- On white backgrounds, hollow text should use a darker stroke that remains readable.
- In the homepage hero, `WITH` should be hollow and `PURPOSE.` should be solid.

### Section eyebrow marks

- Avoid decorative chip shapes next to eyebrow labels.
- Use a simple thin straight line if an eyebrow accent is needed.
- On black sections, the line can be lime.
- On white sections, the line should be black or another readable dark value.

### Navigation and mega menu

- Top navigation should include: For Military, For Companies, About, Resources.
- Right-side nav should include S2S Core Login and Apply Now.
- Mega menus can borrow the interaction pattern of a large dropdown, but the visuals must feel original to S2S.
- Menu icons should not directly mimic 7 Eagle's icon tile format.
- Current preferred direction: custom S2S icons in parallelogram tiles, with lime hover states.
- Mega menu descriptions must use readable Barlow sizing and contrast.

### Footer

- Footer should appear sitewide.
- Do not include the large `HIRE WITH PURPOSE.` footer tagline.
- Do not use the S2 icon in the footer lockup.
- Footer link text, labels, and social icons should be large enough and bright enough on black.
- The S2 icon can be used as a favicon once the real asset is available.

### Forms and conversion

- Calendly should remain on the military and company pages after lead capture or as the initial-call destination.
- Company scheduling URL: `https://calendly.com/davidhester/s2s-hiring`.
- Patrick's military Calendly URL is still needed.
- ActiveCampaign form IDs are still needed.
- Recommended flow: short native form, then a thank-you state with Calendly booking.
- Avoid sending high-intent users away to an external landing page unless the off-site tool is required.

### Stats and claims

- Employment rate: `96%`.
- Training contributed: `$330K` in 2025.
- ROI: standardize to `8x` when using a single headline stat.
- Do not say `0 ramp time`.
- Use `0 added headcount burden during ramp` or equivalent wording.
- Remove unverified social proof numbers, such as invented newsletter subscriber counts.

### Copy polish

- Remove AI-looking em dashes from marketing copy.
- Use periods, commas, colons, or rewritten sentences instead of mechanical dash replacement.
- Keep en dashes where grammatically correct for numeric ranges, such as `3-4 month` only if the site style prefers hyphens, or `3-4` if ASCII-only is required.
- Keep grammar natural and direct.

## Page-specific checks

### Home

- Hero stats should use larger numbers and readable captions.
- Audience cards above Results should not be visually blown out by white images. Preferred treatment: subdued default image state, stronger hover reveal.
- `Results That Speak For Themselves` should have readable labels and captions on white.
- `Compress Ramp. Generate Pipeline.` should not use competing double green lines near `THE BUSINESS CASE`.
- `S2S Internship Model` should be highlighted with green text only.
- Newsletter section needs stronger value copy and readable form styling.

### Military

- Hero should include the empathy line: `Your mission doesn't end when you leave the military. It evolves.`
- Include RateMySkillBridge when live: `https://ratemyskb.com/company/service-2-software`.
- Military form should use the same readable dark-form treatment as the company form when placed on black.
- CTA language should consistently use `Apply Now`.

### Companies

- Hero should lead with the ROI/value framing around one-third cost.
- `ONE-THIRD` should remain hollow but pop with a bright white outline if it sits on a dark image.
- `Your Competitors Are Still Guessing` should be a white section if it follows the dark company hero.
- ROI calculator should live in the company page after partner-results proof and before the process/steps section, unless moved closer to the booking form for conversion testing.
- ROI calculator should match S2S branding and work on a black section.
- CTA language should consistently use `Schedule a Call`.

### About

- Preserve the belief-system copy around `Sales Is the Bridge Between Service and Success`.
- About page team and founder sections should share the same typography and contrast rules as the rest of the site.

### Blog and Resources

- Blog cards should link to real article pages.
- Article body copy should prioritize readability over visual compression.
- Blog pages should eventually become indexable standalone URLs, not only in-page SPA states.

## Known open inputs

- Latest Claude-generated `index.html`.
- TT Lakes webfont file or approved hosted font path.
- Real favicon/icon asset.
- Patrick's Calendly URL.
- ActiveCampaign form IDs.
- Real ROI calculator program cost.
- S2S Core portal URL.
- Final logo.dev token/domain list, if logo.dev remains in production.
