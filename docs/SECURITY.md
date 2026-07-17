# Website security scan

Scan date: 2026-07-16  
Source: Dave’s `index (7).html` (Slack) hardened into `index.html`

## Summary

Static marketing SPA with lead forms that POST to ActiveCampaign and open Calendly. No secrets were found in the HTML. Gaps below were fixed in-repo or deferred with clear follow-ups.

## Findings

| Severity | Finding | Status |
| --- | --- | --- |
| Medium | No Content-Security-Policy / security headers | Fixed — CSP meta in `index.html`; CloudFront response headers policy in `infra/` |
| Medium | `innerHTML` used for confirmation copy (XSS footgun) | Fixed — switched to `textContent` |
| Low | External `target="_blank"` links without `rel="noopener noreferrer"` | Fixed |
| Low | Testimonial iframe had no sandbox / referrer policy | Fixed — sandbox + referrerpolicy |
| Low | ActiveCampaign form IDs still placeholders (`TODO_AC_FORM_ID`) | Fixed — wired to forms 11/12/13 |
| Info | Calendly script loaded without SRI | Accepted — third-party widget; CSP allowlists origin |
| Info | `mode: 'no-cors'` AC POSTs | Expected for AC `proc.php`; response opaque by design |
| Info | Inline scripts/styles require `'unsafe-inline'` in CSP | Accepted for single-file SPA; tighten if/when assets are split |

## Third-party surfaces

- `service2software.activehosted.com` — form posts
- `assets.calendly.com` / `calendly.com` — booking widget
- `embed-v2.testimonial.to` — testimonials iframe
- `fonts.googleapis.com` / `fonts.gstatic.com` — fonts
- `images.unsplash.com` — stock imagery

## Infrastructure controls (AWS)

When deployed via `infra/` CDK:

- Private S3 bucket, Block Public Access on
- CloudFront + Origin Access Control (no public bucket)
- HTTPS only, TLS 1.2+, HTTP→HTTPS redirect
- Response headers: CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options: DENY`
- SSE-S3 encryption at rest

## Checkov (CloudFormation) notes

Synthesized stack passed core S3/CloudFront hardening checks (private bucket,
HTTPS redirect, OAC path, access logging). Remaining fails are accepted for
this static marketing site:

- Log bucket itself without versioning / nested logging (normal for log sinks)
- CDK `BucketDeployment` Lambda custom resource (managed by AWS CDK; VPC/DLQ
  not applicable)
- CloudFront WAF not attached by default (add AWS WAF if/when abuse appears)
- Viewer-certificate TLS check can false-positive on the default `*.cloudfront.net`
  cert; stack sets `minimumProtocolVersion: TLS_V1_2_2021`

## ActiveCampaign forms (wired)

Public form posts go to `service2software.activehosted.com/proc.php`. No API key
is embedded in the site — only public form `u`/`f` (and related) fields.

| Site form | AC form | `u` / `f` |
| --- | --- | --- |
| Military Application (home + military) | Military Application | 11 |
| Partner Inquiry (home + companies) | Partner Inquiry | 12 |
| Newsletter | Home Page Group | 13 |

Custom fields used: `field[5]` Branch, `field[32]` ETS window, `field[35]` Company,
`field[34]` Hiring roles. Newsletter list: **Home Page Group**.

## Remaining ops TODOs

1. Point S2S Core / Candidate portal links to production URLs.
2. Configure GitHub Actions secrets / OIDC for AWS deploy (see README).
3. Attach custom domain (`service2software.org`) + ACM cert in us-east-1.
4. Optional: attach AWS WAF WebACL to the CloudFront distribution.
