# Website Branching Strategy

The repository starts from `main`. Feature branches must follow the cloud-agent naming rule:

`cursor/<descriptive-name>-0fa3`

## Recommended workflow

1. Import or scaffold the current site on one bootstrap branch.
2. Merge the bootstrap PR first so every later branch has the same baseline.
3. Create one branch per page for page-level structure and shared copy decisions.
4. Create section branches only when a section is large enough to review independently.
5. Keep shared styling fixes in a shared brand-system branch instead of repeating them in page branches.

## Why not create every branch immediately

Git branches should point to reviewable code states. Creating dozens of empty branches before the HTML is imported will add bookkeeping without improving review quality.

The practical version of the user's request is:

- One baseline branch for importing the current Claude HTML.
- One shared brand-system branch for global typography, CTA, color, nav, footer, and form rules.
- Page branches for Home, Military, Companies, About, and Blog/Resources.
- Optional section branches under each page when a section has meaningful copy, layout, or conversion work.

## Baseline branches

| Purpose | Branch |
| --- | --- |
| Repo bootstrap and audit docs | `cursor/website-branding-bootstrap-0fa3` |
| Import latest Claude HTML and assets | `cursor/import-current-site-0fa3` |
| Sitewide brand system cleanup | `cursor/sitewide-brand-system-0fa3` |

## Page branches

| Page | Branch |
| --- | --- |
| Home | `cursor/home-page-0fa3` |
| Military | `cursor/military-page-0fa3` |
| Companies | `cursor/companies-page-0fa3` |
| About | `cursor/about-page-0fa3` |
| Blog and Resources | `cursor/blog-resources-0fa3` |

## Section branches

Create these after the page branch exists and only when the section needs standalone review.

### Home

- `cursor/home-hero-0fa3`
- `cursor/home-audience-cards-0fa3`
- `cursor/home-results-0fa3`
- `cursor/home-ramp-pipeline-0fa3`
- `cursor/home-stories-0fa3`
- `cursor/home-newsletter-0fa3`

### Military

- `cursor/military-hero-0fa3`
- `cursor/military-program-0fa3`
- `cursor/military-apply-flow-0fa3`
- `cursor/military-testimonials-0fa3`
- `cursor/military-calendly-0fa3`

### Companies

- `cursor/companies-hero-0fa3`
- `cursor/companies-partner-results-0fa3`
- `cursor/companies-roi-calculator-0fa3`
- `cursor/companies-process-0fa3`
- `cursor/companies-booking-flow-0fa3`

### About

- `cursor/about-belief-system-0fa3`
- `cursor/about-founder-0fa3`
- `cursor/about-team-0fa3`
- `cursor/about-principles-0fa3`

### Blog and Resources

- `cursor/blog-index-0fa3`
- `cursor/blog-article-template-0fa3`
- `cursor/blog-seo-urls-0fa3`
- `cursor/resources-mega-menu-0fa3`

## Review checklist for each branch

- Does the branch touch only the intended page or section?
- Are shared design changes moved to the brand-system branch?
- Are copy changes free of em dashes and unverified claims?
- Are fonts consistent with the brand audit?
- Are CTA labels consistent with the target audience?
- Is contrast readable on both black and white sections?
- Does the page still follow black-first section alternation?
- Do links, forms, and calculators work after the change?
