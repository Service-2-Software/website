# Website security & pre-launch scan

Scan date: 2026-08-12 (pre-launch)  
Prior scan: 2026-07-16  
Source: `index.html` + `infra/` CDK (S3 + CloudFront) + `.github/workflows/deploy-aws.yml`

## Summary

Static marketing SPA with lead forms that POST to ActiveCampaign and open Calendly. No secrets were found in the HTML or infra. Hosting controls from the July hardening pass remain in place. This pass focused on go-live readiness: re-verified security posture and fixed the main performance risk (1.7 MB monolithic HTML with inline base64).

**Verdict:** Safe to go live from a hosting/security-headers perspective once ops TODOs below are confirmed. Largest remaining launch risks are product/content placeholders (portal URL, ROI assumption, review copy)—not exploit surface.

## Security findings

| Severity | Finding | Status |
| --- | --- | --- |
| Medium | No Content-Security-Policy / security headers | Fixed — CSP meta in `index.html`; CloudFront response headers policy in `infra/` (meta ↔ header CSP in sync) |
| Medium | `innerHTML` used for confirmation copy (XSS footgun) | Fixed — `textContent` only |
| Low | External `target="_blank"` links without `rel="noopener noreferrer"` | Fixed |
| Low | Testimonial iframe had no sandbox / referrer policy | Fixed — sandbox + referrerpolicy |
| Low | ActiveCampaign form IDs still placeholders | Fixed — forms 11/12/13 |
| Low | No explicit `Cache-Control` on deploy | Fixed (2026-08-12) — HTML `max-age=60, must-revalidate`; `/assets/*` `max-age=86400, must-revalidate` |
| Info | Calendly script loaded without SRI | Accepted — third-party widget; CSP allowlists origin |
| Info | `mode: 'no-cors'` AC POSTs | Expected for AC `proc.php`; response opaque by design |
| Info | Inline scripts/styles require `'unsafe-inline'` in CSP | Accepted for single-file SPA; tighten if/when assets are split |
| Info | HSTS `preload` on default `*.cloudfront.net` cert | Acceptable; keep when attaching `service2software.org` + ACM |
| Info | No AWS WAF on CloudFront | Optional — add if abuse/bot traffic appears |
| Info | Name/email prefilled into Calendly popup URL | Expected UX; data goes to Calendly after user submits a form |

### Cookie consent & analytics

- Banner stores `s2s_cookie_consent` in `localStorage` (`granted` / `denied`).
- GA4 Consent Mode defaults deny `analytics_storage` until Accept.
- `S2S_GA_ID` = `G-SK3FHELY0M`; gtag loads only after accept; SPA `page_view` gated on consent.
- Decline / Cookie Settings updates consent to denied and stops further page_view events (script already loaded is not unloaded—standard for GA Consent Mode).

### Third-party surfaces

- `service2software.activehosted.com` — form posts (public form `u`/`f` only; no API key)
- `assets.calendly.com` / `calendly.com` — booking widget
- `embed-v2.testimonial.to` — testimonials iframe
- `fonts.googleapis.com` / `fonts.gstatic.com` — fonts (weights trimmed 2026-08-12)
- `images.unsplash.com` — stock imagery
- `www.googletagmanager.com` / `*.google-analytics.com` — GA4 (consent-gated)
- `app.gohighlevel.com` — interim Candidate Login links (navigation only; not in CSP script/connect allowlists)

### Infrastructure controls (AWS)

- Private S3 bucket, Block Public Access on, SSE-S3, versioned site bucket
- CloudFront + Origin Access Control
- HTTPS only, TLS 1.2+, HTTP→HTTPS redirect, HTTP/2 + HTTP/3, edge compression
- Response headers: CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options: DENY`
- Access logging to dedicated log bucket (90-day expiry)
- CI deploy via GitHub Actions OIDC (no long-lived AWS keys in repo)

### Checkov notes (unchanged)

Accepted for this static marketing site: log-bucket nesting/versioning, CDK `BucketDeployment` Lambda CR, WAF optional, default cert TLS false-positives (stack forces TLS 1.2).

### Supply chain (infra)

`npm audit` in `infra/` reports a high severity `brace-expansion` DoS advisory inside the bundled `aws-cdk-lib` dependency tree. It affects CDK synth/deploy tooling only (not the public website). Track an `aws-cdk-lib` upgrade when upstream ships a fixed bundle.

## ActiveCampaign forms (wired)

Public form posts go to `service2software.activehosted.com/proc.php`.

| Site form | AC form | `u` / `f` |
| --- | --- | --- |
| Military Application (home + military) | Military Application | 11 |
| Partner Inquiry (home + companies) | Partner Inquiry | 12 |
| Newsletter | Home Page Group | 13 |

## Optimization findings (2026-08-12)

| Priority | Finding | Action |
| --- | --- | --- |
| P0 | `index.html` was ~1.75 MB (mostly inline base64 heroes/logos) | Extracted images to `assets/media/` (content-hashed); HTML ~207 KB (~50 KB gzip) |
| P0 | Logo ticker duplicated 28 logos in HTML for infinite scroll | HTML embeds once; JS clones the track |
| P1 | Google Fonts loaded many unused weights; CSS used `font-weight:900` without a 900 file | Oswald 600/700 + Barlow 300/400/600; map 900→700 |
| P1 | Most Unsplash images loaded eagerly | `loading="lazy"` + `decoding="async"`; home LCP hero gets `fetchpriority="high"` |
| P1 | No Cache-Control on S3 objects | Split BucketDeployments with HTML vs `/assets` TTLs |
| P2 | No `prefers-reduced-motion` | Pause ticker / skip reveal motion when requested |
| Later | Still a single HTML document for all routes | Optional: split pages or defer off-route media |
| Later | Calendly CSS/JS on every visit | Optional: load on first booking CTA |

## Remaining ops / content TODOs (launch checklist)

1. **Point S2S Core / Candidate portal links to production URLs** (nav `S2S Core Login` is still `#`; mega/footer still use GoHighLevel interim).
2. Confirm GitHub Actions secrets / OIDC (`AWS_DEPLOY_ROLE_ARN`, `AWS_ACCOUNT_ID`) and that deploy to `main` succeeds.
3. Attach custom domain (`service2software.org`) + ACM cert in `us-east-1`.
4. Optional: attach AWS WAF WebACL to the CloudFront distribution.
5. Replace ROI calculator `programCost: 25000` TODO with real annual partnership investment.
6. Paste exact RateMySKB review text (About page TODO).
7. Optional Canva photo swaps marked in HTML comments.
