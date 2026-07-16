# Website infrastructure (CDK)

Deploys the static site in the repo root to:

- Private S3 bucket (SSE-S3, Block Public Access, TLS-only bucket policy)
- CloudFront distribution with Origin Access Control
- Security response headers (CSP, HSTS, `X-Frame-Options: DENY`, etc.)

## Commands

```bash
npm ci
npx cdk synth
npx cdk diff
npx cdk deploy
```

Outputs: `WebsiteUrl`, `DistributionId`, `BucketName`.
