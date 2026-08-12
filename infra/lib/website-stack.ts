import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import * as wafv2 from "aws-cdk-lib/aws-wafv2";
import { Construct } from "constructs";

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

    const siteDomain = (process.env.SITE_DOMAIN || "").trim();
    const wwwDomain =
      (process.env.SITE_WWW_DOMAIN || "").trim() ||
      (siteDomain ? `www.${siteDomain}` : "");
    const certificateArn = (process.env.ACM_CERTIFICATE_ARN || "").trim();
    const domainNames = [siteDomain, wwwDomain].filter(Boolean);
    const useCustomDomain = Boolean(certificateArn && domainNames.length);

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

    // CloudFront-scoped WAF (must live in us-east-1 with the distribution).
    const webAcl = new wafv2.CfnWebACL(this, "WebAcl", {
      name: `s2s-website-${this.stackName}`,
      description: "AWS managed rules for S2S marketing CloudFront distribution",
      scope: "CLOUDFRONT",
      defaultAction: { allow: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "s2sWebsiteWebAcl",
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: "AWSManagedRulesCommonRuleSet",
          priority: 1,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: "AWS",
              name: "AWSManagedRulesCommonRuleSet",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "s2sCommonRules",
            sampledRequestsEnabled: true,
          },
        },
        {
          name: "AWSManagedRulesKnownBadInputsRuleSet",
          priority: 2,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: "AWS",
              name: "AWSManagedRulesKnownBadInputsRuleSet",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "s2sKnownBadInputs",
            sampledRequestsEnabled: true,
          },
        },
        {
          name: "AWSManagedRulesAmazonIpReputationList",
          priority: 3,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: "AWS",
              name: "AWSManagedRulesAmazonIpReputationList",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "s2sIpReputation",
            sampledRequestsEnabled: true,
          },
        },
      ],
    });

    const certificate = useCustomDomain
      ? acm.Certificate.fromCertificateArn(
          this,
          "SiteCertificate",
          certificateArn
        )
      : undefined;

    const distribution = new cloudfront.Distribution(this, "Distribution", {
      comment: "Service 2 Software website",
      defaultRootObject: "index.html",
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      httpVersion: cloudfront.HttpVersion.HTTP2_AND_3,
      priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
      enableLogging: true,
      logBucket: accessLogsBucket,
      logFilePrefix: "cloudfront/",
      webAclId: webAcl.attrArn,
      domainNames: useCustomDomain ? domainNames : undefined,
      certificate,
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

    const cfnDistribution = distribution.node
      .defaultChild as cloudfront.CfnDistribution;

    if (!useCustomDomain) {
      // Explicit TLS floor for the default *.cloudfront.net cert (Checkov CKV_AWS_174).
      cfnDistribution.addPropertyOverride(
        "DistributionConfig.ViewerCertificate",
        {
          CloudFrontDefaultCertificate: true,
          MinimumProtocolVersion: "TLSv1.2_2021",
        }
      );
    }

    const siteRoot = path.join(__dirname, "..", "..");

    // HTML/root: short TTL so content updates show quickly after deploy+invalidation.
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
            "assets/**",
            "assets",
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
      cacheControl: [
        s3deploy.CacheControl.fromString(
          "public, max-age=60, must-revalidate"
        ),
      ],
    });

    // Static media under /assets: longer browser cache (CloudFront still
    // invalidated on deploy). Filenames are content-hashed where extracted.
    new s3deploy.BucketDeployment(this, "DeployAssets", {
      sources: [s3deploy.Source.asset(path.join(siteRoot, "assets"))],
      destinationBucket: siteBucket,
      destinationKeyPrefix: "assets",
      distribution,
      distributionPaths: ["/assets/*"],
      memoryLimit: 512,
      prune: false,
      // Team headshots reuse stable filenames; avoid immutable so updates
      // appear within a day without requiring rename/hash churn.
      cacheControl: [
        s3deploy.CacheControl.fromString(
          "public, max-age=86400, must-revalidate"
        ),
      ],
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
      description: "CloudFront domain (CNAME target for custom domain)",
    });
    new cdk.CfnOutput(this, "WebsiteUrl", {
      value: useCustomDomain
        ? `https://${wwwDomain || siteDomain}`
        : `https://${distribution.distributionDomainName}`,
    });
    new cdk.CfnOutput(this, "WebAclArn", {
      value: webAcl.attrArn,
      description: "WAFv2 WebACL attached to CloudFront",
    });
    if (useCustomDomain) {
      new cdk.CfnOutput(this, "CustomDomainNames", {
        value: domainNames.join(", "),
      });
      new cdk.CfnOutput(this, "CertificateArn", {
        value: certificateArn,
      });
    } else {
      new cdk.CfnOutput(this, "CustomDomainStatus", {
        value:
          "Set GitHub vars SITE_DOMAIN=service2software.org and ACM_CERTIFICATE_ARN=<us-east-1 ACM ARN>, then redeploy. Point Cloudflare DNS to DistributionDomainName.",
      });
    }
  }
}
