#!/bin/bash

# Deploy Backend to AWS App Runner
# This script creates an App Runner service for the Flask backend

set -e

# Configuration
SERVICE_NAME="deepscribe-backend"
REGION="us-east-1"
ROLE_ARN=""  # Will be set automatically if not provided

echo "🚀 Deploying Flask Backend to AWS App Runner..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $ACCOUNT_ID"

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

    # Attach basic execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

    # Clean up
    rm trust-policy.json
    
    echo "✅ IAM role created successfully"
else
    echo "✅ IAM role already exists"
fi

# Get role ARN
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

# Check if service already exists
if aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" &>/dev/null; then
    echo "🔄 Service exists. Updating..."
    
    # Update existing service
    aws apprunner update-service \
        --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" \
        --source-configuration '{
            "AutoDeploymentsEnabled": true,
            "CodeRepository": {
                "RepositoryUrl": "https://github.com/'$(git remote get-url origin | sed 's/.*github.com[:/]\([^.]*\).*/\1/')'",
                "SourceCodeVersion": {
                    "Type": "BRANCH",
                    "Value": "main"
                },
                "CodeConfiguration": {
                    "ConfigurationSource": "REPOSITORY"
                }
            }
        }' \
        --instance-configuration '{
            "Cpu": "0.25 vCPU",
            "Memory": "0.5 GB",
            "InstanceRoleArn": "'$ROLE_ARN'"
        }'
        
    SERVICE_ARN="arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME"
else
    echo "🆕 Creating new App Runner service..."
    
    # Create new service
    SERVICE_ARN=$(aws apprunner create-service \
        --service-name $SERVICE_NAME \
        --source-configuration '{
            "AutoDeploymentsEnabled": true,
            "CodeRepository": {
                "RepositoryUrl": "https://github.com/'$(git remote get-url origin | sed 's/.*github.com[:/]\([^.]*\).*/\1/')'",
                "SourceCodeVersion": {
                    "Type": "BRANCH",
                    "Value": "main"
                },
                "CodeConfiguration": {
                    "ConfigurationSource": "REPOSITORY"
                }
            }
        }' \
        --instance-configuration '{
            "Cpu": "0.25 vCPU",
            "Memory": "0.5 GB",
            "InstanceRoleArn": "'$ROLE_ARN'"
        }' \
        --query 'Service.ServiceArn' \
        --output text)
fi

echo "📍 Service ARN: $SERVICE_ARN"

# Wait for service to be ready
echo "⏳ Waiting for service to be running..."
aws apprunner wait service-running --service-arn $SERVICE_ARN

# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --query 'Service.ServiceUrl' \
    --output text)

echo "✅ Backend deployment completed!"
echo "🌐 Backend URL: https://$SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Update .env.production with: NEXT_PUBLIC_API_URL=https://$SERVICE_URL"
echo "2. Test the backend health endpoint: curl https://$SERVICE_URL/api/health"
echo "3. Deploy the frontend using deploy-frontend.sh"
echo ""
echo "💡 To update .env.production automatically, run:"
echo "   sed -i '' 's|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=https://$SERVICE_URL|' .env.production"