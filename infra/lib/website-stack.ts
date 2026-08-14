import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

/**
 * Public domains served by this distribution. CloudFront requires the ACM
 * certificate to live in us-east-1 and to cover every name listed here.
 */
const SITE_DOMAIN_NAMES = ["service2software.org", "www.service2software.org"];

/**
 * ACM certificate (us-east-1) covering the domains above. Override via the
 * `certificateArn` CDK context value if the certificate is ever reissued.
 */
const DEFAULT_CERTIFICATE_ARN =
  "arn:aws:acm:us-east-1:483013639442:certificate/07b71d16-5f23-4982-908d-74b65d35af3c";

/** CSP aligned with docs/SECURITY.md and index.html meta CSP. */
const CONTENT_SECURITY_POLICY = [
  "default-src 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "frame-ancestors 'none'",
  "form-action 'self' https://service2software.activehosted.com",
  "script-src 'self' 'unsafe-inline' https://assets.calendly.com https://www.googletagmanager.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://assets.calendly.com",
  "font-src 'self' data: https://fonts.gstatic.com",
  "img-src 'self' data: https://images.unsplash.com https://www.google-analytics.com https://www.googletagmanager.com",
  "connect-src 'self' https://service2software.activehosted.com https://calendly.com https://*.calendly.com https://assets.calendly.com https://www.google-analytics.com https://*.google-analytics.com https://analytics.google.com https://*.analytics.google.com https://www.googletagmanager.com",
  "frame-src https://calendly.com https://*.calendly.com https://embed-v2.testimonial.to https://testimonial.to",
  "upgrade-insecure-requests",
].join("; ");

export class WebsiteStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const accessLogsBucket = new s3.Bucket(this, "AccessLogsBucket", {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      lifecycleRules: [
        {
          id: "expire-access-logs",
          expiration: cdk.Duration.days(90),
        },
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
    });

    const siteBucket = new s3.Bucket(this, "SiteBucket", {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      versioned: true,
      serverAccessLogsBucket: accessLogsBucket,
      serverAccessLogsPrefix: "s3-access/",
      // Site content is regenerated from git; retain on stack delete for safety.
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
    });

    const responseHeadersPolicy = new cloudfront.ResponseHeadersPolicy(
      this,
      "SecurityHeaders",
      {
        responseHeadersPolicyName: `s2s-website-security-${this.stackName}`,
        comment: "HSTS, CSP, and browser hardening for S2S marketing site",
        securityHeadersBehavior: {
          contentSecurityPolicy: {
            contentSecurityPolicy: CONTENT_SECURITY_POLICY,
            override: true,
          },
          contentTypeOptions: { override: true },
          frameOptions: {
            frameOption: cloudfront.HeadersFrameOption.DENY,
            override: true,
          },
          referrerPolicy: {
            referrerPolicy:
              cloudfront.HeadersReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN,
            override: true,
          },
          strictTransportSecurity: {
            accessControlMaxAge: cdk.Duration.days(365),
            includeSubdomains: true,
            preload: true,
            override: true,
          },
          xssProtection: { protection: true, modeBlock: true, override: true },
        },
        customHeadersBehavior: {
          customHeaders: [
            {
              header: "Permissions-Policy",
              value:
                "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
              override: true,
            },
          ],
        },
      }
    );

    const certificateArn =
      (this.node.tryGetContext("certificateArn") as string | undefined) ??
      DEFAULT_CERTIFICATE_ARN;
    const certificate = acm.Certificate.fromCertificateArn(
      this,
      "SiteCertificate",
      certificateArn
    );

    const distribution = new cloudfront.Distribution(this, "Distribution", {
      comment: "Service 2 Software website",
      defaultRootObject: "index.html",
      domainNames: SITE_DOMAIN_NAMES,
      certificate,
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      httpVersion: cloudfront.HttpVersion.HTTP2_AND_3,
      priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
      enableLogging: true,
      logBucket: accessLogsBucket,
      logFilePrefix: "cloudfront/",
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(siteBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
        compress: true,
        responseHeadersPolicy,
      },
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.minutes(5),
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.minutes(5),
        },
      ],
    });

    const siteRoot = path.join(__dirname, "..", "..");

    new s3deploy.BucketDeployment(this, "DeployWebsite", {
      sources: [
        s3deploy.Source.asset(siteRoot, {
          exclude: [
            "infra/**",
            "infra",
            ".git/**",
            ".git",
            ".github/**",
            ".github",
            "docs/**",
            "docs",
            "node_modules/**",
            "node_modules",
            "*.md",
            ".gitignore",
            ".env*",
          ],
        }),
      ],
      destinationBucket: siteBucket,
      distribution,
      distributionPaths: ["/*"],
      memoryLimit: 512,
    });

    new cdk.CfnOutput(this, "BucketName", {
      value: siteBucket.bucketName,
      description: "Private S3 bucket holding site assets",
    });
    new cdk.CfnOutput(this, "DistributionId", {
      value: distribution.distributionId,
    });
    new cdk.CfnOutput(this, "DistributionDomainName", {
      value: distribution.distributionDomainName,
      description: "CloudFront distribution domain (point site DNS CNAMEs here)",
    });
    new cdk.CfnOutput(this, "WebsiteUrl", {
      value: `https://${SITE_DOMAIN_NAMES[1]}`,
      description: "Primary public site URL served via the custom domain",
    });
  }
}
