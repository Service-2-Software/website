#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { WebsiteStack } from "../lib/website-stack";

const app = new cdk.App();

const account = process.env.CDK_DEFAULT_ACCOUNT;
const region = process.env.CDK_DEFAULT_REGION || "us-east-1";

new WebsiteStack(app, "S2sWebsiteStack", {
  env: account ? { account, region } : { region },
  description: "Service 2 Software marketing site — S3 + CloudFront",
  tags: {
    Project: "s2s-website",
    ManagedBy: "cdk",
  },
});
