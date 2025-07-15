#!/bin/bash

# Simple Backend Deployment to AWS App Runner using local source
# This script creates a source bundle and deploys it

set -e

# Configuration
SERVICE_NAME="deepscribe-backend"
REGION="us-east-1"
SOURCE_BUNDLE="backend-source.zip"

echo "🚀 Deploying Flask Backend to AWS App Runner (local source)..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Create source bundle excluding unnecessary files
echo "📦 Creating source bundle..."
zip -r $SOURCE_BUNDLE . \
    -x "node_modules/*" \
    -x ".next/*" \
    -x "*.git*" \
    -x "*.env*" \
    -x "*.log" \
    -x "deploy-*.sh" \
    -x "Dockerfile" \
    -x "*.md" \
    -x "frontend-source.zip" \
    -x "backend-source.zip"

echo "✅ Source bundle created: $SOURCE_BUNDLE"

# Upload to S3 bucket (create if doesn't exist)
BUCKET_NAME="deepscribe-apprunner-source-$(date +%s)"
echo "☁️  Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION

echo "⬆️  Uploading source bundle to S3..."
aws s3 cp $SOURCE_BUNDLE s3://$BUCKET_NAME/

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create IAM role for App Runner if it doesn't exist
ROLE_NAME="AppRunnerInstanceRole"
if ! aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
    echo "🔐 Creating IAM role for App Runner..."
    
    # Create trust policy
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "tasks.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    # Create the role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json

    # Clean up
    rm trust-policy.json
    
    echo "✅ IAM role created successfully"
fi

# Get role ARN
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

# Create App Runner service using AWS CLI
echo "🆕 Creating App Runner service..."

# Create service configuration file
cat > service-config.json << EOF
{
    "ServiceName": "$SERVICE_NAME",
    "SourceConfiguration": {
        "ImageRepository": {
            "ImageIdentifier": "public.ecr.aws/aws-containers/hello-app-runner:latest",
            "ImageConfiguration": {
                "Port": "8000"
            },
            "ImageRepositoryType": "ECR_PUBLIC"
        },
        "AutoDeploymentsEnabled": false
    },
    "InstanceConfiguration": {
        "Cpu": "0.25 vCPU",
        "Memory": "0.5 GB",
        "InstanceRoleArn": "$ROLE_ARN"
    }
}
EOF

# Check if service already exists
if aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" &>/dev/null; then
    echo "❌ Service already exists. Please delete it first or use a different name."
    exit 1
fi

# For now, let's provide manual instructions
echo "📋 Manual deployment steps:"
echo "1. Go to AWS App Runner console: https://console.aws.amazon.com/apprunner/"
echo "2. Click 'Create service'"
echo "3. Choose 'Source code repository' -> 'Browse for source bundle'"
echo "4. Upload the file: $SOURCE_BUNDLE"
echo "5. Runtime: Python 3"
echo "6. Use the apprunner-backend.yaml configuration"
echo "7. Set environment variables for API keys"
echo ""
echo "📄 Source bundle ready: $SOURCE_BUNDLE"
echo "🗑️  Clean up: rm $SOURCE_BUNDLE"

# Clean up
rm -f service-config.json