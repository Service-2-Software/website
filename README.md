# Service 2 Software — Website

Marketing site for **Service 2 Software (S2S)** — Hire With Purpose.

This branch ships Dave’s latest single-file HTML (`index.html`) plus AWS hosting
infra (private S3 + CloudFront) and a security hardening pass. See
[`docs/SECURITY.md`](docs/SECURITY.md).

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Each page has its own URL (`/military`, `/companies`, `/about`, `/resources`,
`/privacy`, `/resources/<article>`); in-page sections append `#anchors`
(e.g. `/military#mil-cal`). In production CloudFront serves `index.html` for
unknown paths, so deep links work. The basic server above 404s if you refresh
on a deep link; to mirror CloudFront locally, use a fallback server:

```bash
python3 -c "
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
class H(SimpleHTTPRequestHandler):
    def send_error(self, code, *a, **k):
        if code == 404:
            self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        return SimpleHTTPRequestHandler.send_error(self, code, *a, **k)
ThreadingHTTPServer(('127.0.0.1', 8000), H).serve_forever()
"
```

## AWS architecture

| Piece | Choice | Why |
| --- | --- | --- |
| Storage | S3 (private, Block Public Access) | Static assets only |
| CDN | CloudFront + OAC | HTTPS, edge cache, no public bucket |
| Headers | CloudFront response headers policy | CSP, HSTS, frame deny, etc. |
| IaC | AWS CDK (TypeScript) in `infra/` | Repeatable, reviewable deploys |
| CI | GitHub Actions + OIDC | No long-lived AWS keys in GitHub |

**Rough cost (dev / light traffic):** CloudFront + S3 typically stays in the
low single-digit USD/month until traffic grows; custom domain/ACM cert is free.

## Deploy

### One-time AWS setup

1. Create an IAM role for GitHub OIDC that can deploy this stack  
   (`cloudformation:*`, `s3:*`, `cloudfront:*`, `iam:PassRole` scoped as needed).
2. In the GitHub repo, set:
   - Secret `AWS_DEPLOY_ROLE_ARN`
   - Secret `AWS_ACCOUNT_ID`
   - Optional variable `AWS_REGION` (default `us-east-1`)
3. Bootstrap CDK once in the account/region:

```bash
cd infra
npm ci
npx cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
```

### Manual deploy (local)

```bash
cd infra
npm ci
export CDK_DEFAULT_ACCOUNT=...
export CDK_DEFAULT_REGION=us-east-1
npx cdk deploy
```

CloudFront URL is printed as `WebsiteUrl`. Attach `service2software.org` later
with an ACM certificate in `us-east-1`.

### CI deploy

Push to `main` (or run **Deploy website to AWS** via `workflow_dispatch`).

## Security

Hardening applied in `index.html` + CloudFront:

- CSP + referrer policy
- No `innerHTML` for confirmation strings
- `rel="noopener noreferrer"` on external tabs
- Sandboxed testimonials iframe
- Private origin, TLS 1.2+, HSTS

Open product TODO (not a hosting blocker): production Core portal URL.
ActiveCampaign lead forms are wired (`docs/SECURITY.md`).

## Cookie consent & visitor analytics

A cookie banner appears on first visit. Visitors can accept analytics or keep essential-only.
Choice is stored in `localStorage` and can be changed via footer **Cookie Settings**.

**Traffic analytics:** GA4 Measurement ID `G-SK3FHELY0M` is set in `index.html` (`S2S_GA_ID`). GA loads only after the visitor accepts analytics cookies.

Lead/CRM data (names, emails from forms) continues to flow into ActiveCampaign separately from page analytics.
CloudFront access logs in AWS provide basic request-level traffic for ops/security.
