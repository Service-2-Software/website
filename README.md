# Service 2 Software — Website

Marketing site for **Service 2 Software (S2S)** — Hire With Purpose.

This branch ships the marketing site (`index.html` + `assets/`) plus AWS hosting
infra (private S3 + CloudFront) and a security/perf hardening pass. See
[`docs/SECURITY.md`](docs/SECURITY.md) for the latest pre-launch scan.

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## AWS architecture

| Piece | Choice | Why |
| --- | --- | --- |
| Storage | S3 (private, Block Public Access) | Static assets only |
| CDN | CloudFront + OAC | HTTPS, edge cache, no public bucket |
| WAF | WAFv2 (CloudFront scope) | Managed common / bad-input / IP reputation rules |
| Headers | CloudFront response headers policy | CSP, HSTS, frame deny, etc. |
| TLS / domain | ACM in `us-east-1` + Cloudflare DNS | Custom domain on CloudFront |
| IaC | AWS CDK (TypeScript) in `infra/` | Repeatable, reviewable deploys |
| CI | GitHub Actions + OIDC | No long-lived AWS keys in GitHub |

**Live CloudFront (OIDC deploys verified):** https://d2by6tunn6pa78.cloudfront.net

**Rough cost (dev / light traffic):** CloudFront + S3 typically stays in the
low single-digit USD/month until traffic grows; ACM cert is free; WAF managed
rules add a small monthly fee.

## Deploy

### One-time AWS setup

1. Create an IAM role for GitHub OIDC that can deploy this stack  
   (`cloudformation:*`, `s3:*`, `cloudfront:*`, `acm:*`, `wafv2:*`,
   `iam:PassRole` scoped as needed).
2. In the GitHub repo, set:
   - Secret `AWS_DEPLOY_ROLE_ARN`
   - Secret `AWS_ACCOUNT_ID`
   - Optional variables:
     - `AWS_REGION` (default `us-east-1`)
     - `SITE_DOMAIN` (default `service2software.org`)
     - `SITE_WWW_DOMAIN` (default `www.service2software.org`)
     - `ACM_CERTIFICATE_ARN` (optional override once cert is issued)
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
# Optional custom domain (cert must already be ISSUED in us-east-1):
export SITE_DOMAIN=service2software.org
export SITE_WWW_DOMAIN=www.service2software.org
export ACM_CERTIFICATE_ARN=arn:aws:acm:us-east-1:...:certificate/...
npx cdk deploy
```

### CI deploy

Push to `main` (or run **Deploy website to AWS** via `workflow_dispatch`).

The workflow:

1. Ensures an ACM cert for `service2software.org` + `www` (requests one if missing)
2. Prints DNS validation CNAMEs for Cloudflare
3. Attaches the cert + aliases on CloudFront **only when the cert status is `ISSUED`**
4. Always deploys the site + WAF WebACL

### Custom domain cutover (Cloudflare)

DNS for `service2software.org` is on Cloudflare today (Kajabi origin). After ACM
shows **Issued**:

1. In Cloudflare DNS, point apex + `www` to the stack output `DistributionDomainName`
   (`d2by6tunn6pa78.cloudfront.net` until replaced by a new distribution domain):
   - `CNAME` / ALIAS `service2software.org` → `….cloudfront.net`
   - `CNAME` `www` → `….cloudfront.net`
2. SSL/TLS mode: **Full (strict)**
3. Keep member login on Kajabi: site links use
   `https://service2software.mykajabi.com/login` (S2S Core). Optionally add a
   Cloudflare Page Rule / Worker so `service2software.org/login` still reaches Kajabi.

## Portals

| Link | Production URL |
| --- | --- |
| S2S Core Login | https://service2software.mykajabi.com/login |
| Candidate Portal | https://app.gohighlevel.com |

## Security

Hardening applied in `index.html` + CloudFront:

- CSP + referrer policy
- No `innerHTML` for confirmation strings
- `rel="noopener noreferrer"` on external tabs
- Sandboxed testimonials iframe
- Private origin, TLS 1.2+, HSTS
- CloudFront WAF (managed rule groups)
- Consent-gated GA4

ActiveCampaign lead forms are wired (`docs/SECURITY.md`).

## Cookie consent & visitor analytics

A cookie banner appears on first visit. Visitors can accept analytics or keep essential-only.
Choice is stored in `localStorage` and can be changed via footer **Cookie Settings**.

**Traffic analytics:** GA4 Measurement ID `G-SK3FHELY0M` is set in `index.html` (`S2S_GA_ID`). GA loads only after the visitor accepts analytics cookies.

Lead/CRM data (names, emails from forms) continues to flow into ActiveCampaign separately from page analytics.
CloudFront access logs in AWS provide basic request-level traffic for ops/security.
