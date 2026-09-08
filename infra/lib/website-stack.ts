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

/** Canonical public host (apex). www 301-redirects here, preserving path + query. */
const CANONICAL_DOMAIN_NAME = SITE_DOMAIN_NAMES[0];

/**
 * CloudFront Function (viewer-request): 301 any non-canonical host (www) to the
 * apex, preserving the path and query string. HTTP→HTTPS is still handled by
 * the viewer protocol policy, and requests on the canonical host pass through
 * untouched, so the 403/404→index.html SPA fallback keeps working.
 */
const REDIRECT_TO_APEX_FUNCTION = `
function handler(event) {
  var request = event.request;
  var host = request.headers.host && request.headers.host.value;
  if (host === '${CANONICAL_DOMAIN_NAME}') {
    return request;
  }
  var params = [];
  for (var key in request.querystring) {
    var entry = request.querystring[key];
    if (entry.multiValue) {
      entry.multiValue.forEach(function (item) {
        params.push(item.value === '' ? key : key + '=' + item.value);
      });
    } else if (entry.value === '') {
      params.push(key);
    } else {
      params.push(key + '=' + entry.value);
    }
  }
  var qs = params.length ? '?' + params.join('&') : '';
  return {
    statusCode: 301,
    statusDescription: 'Moved Permanently',
    headers: {
      location: { value: 'https://${CANONICAL_DOMAIN_NAME}' + request.uri + qs },
      'cache-control': { value: 'max-age=3600' },
    },
  };
}
`;

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
  // The ActiveCampaign full form embed on the hidden /sb-application page loads
  // its script from service2software.activehosted.com, intl-tel-input JS/CSS
  // and flag sprites from cdn.jsdelivr.net, fonts from fonts.bunny.net, and
  // images from AC's CDN (d226aj4ao1t61q.cloudfront.net). Keep in sync with
  // the index.html meta CSP.
  "script-src 'self' 'unsafe-inline' https://assets.calendly.com https://www.googletagmanager.com https://b2bjsstore.s3.us-west-2.amazonaws.com https://assets.apollo.io https://d-code.liadm.com https://service2software.activehosted.com https://cdn.jsdelivr.net",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://assets.calendly.com https://fonts.bunny.net https://cdn.jsdelivr.net",
  "font-src 'self' data: https://fonts.gstatic.com https://fonts.bunny.net",
  "img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com https://d226aj4ao1t61q.cloudfront.net https://cdn.jsdelivr.net",
  // RB2B needs app.rb2b.com plus its IP-eligibility check (pro.ip-api.com) and
  // its data-collection API Gateway. The gateway host is pinned exactly; if RB2B
  // rotates it in a script update, collection breaks with a CSP violation —
  // check DevTools console and update both CSPs (here + index.html meta).
  // Apollo website tracker loads from assets.apollo.io, posts events to
  // aplo-evnt.com, and may load LiveIntent (d-code.liadm.com) for identity.
  "connect-src 'self' https://service2software.activehosted.com https://calendly.com https://*.calendly.com https://assets.calendly.com https://www.google-analytics.com https://*.google-analytics.com https://analytics.google.com https://*.analytics.google.com https://www.googletagmanager.com https://app.rb2b.com https://pro.ip-api.com https://9xgnrndqve.execute-api.us-west-2.amazonaws.com https://aplo-evnt.com",
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

    const redirectToApexFunction = new cloudfront.Function(
      this,
      "RedirectToApexFunction",
      {
        comment: "301 www.service2software.org -> service2software.org",
        runtime: cloudfront.FunctionRuntime.JS_2_0,
        code: cloudfront.FunctionCode.fromInline(REDIRECT_TO_APEX_FUNCTION),
      }
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
        functionAssociations: [
          {
            function: redirectToApexFunction,
            eventType: cloudfront.FunctionEventType.VIEWER_REQUEST,
          },
        ],
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
      value: `https://${CANONICAL_DOMAIN_NAME}`,
      description: "Primary public site URL served via the custom domain",
    });
  }
}
