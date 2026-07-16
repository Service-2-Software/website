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

Open product TODOs (not blockers for hosting): ActiveCampaign form IDs,
production Core portal URL. Details in `docs/SECURITY.md`.
