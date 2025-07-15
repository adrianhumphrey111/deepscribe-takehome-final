# 🚀 AWS Deployment Guide for Clinical Trials Matcher

## 📋 Prerequisites

- AWS Account with credits
- AWS CLI configured (`aws configure`)
- Docker installed locally
- Your API keys ready (OpenAI, Anthropic)

## 🎯 Deployment Options

### **Option 1: AWS App Runner (Recommended - Easiest)**

Perfect for getting started quickly with minimal configuration.

#### Steps:
1. **Store API Keys in AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name "clinical-trials/openai-api-key" \
  --secret-string "your-openai-api-key"

aws secretsmanager create-secret \
  --name "clinical-trials/anthropic-api-key" \
  --secret-string "your-anthropic-api-key"
```

2. **Deploy Backend to App Runner:**
   - Go to AWS Console → App Runner
   - Create service from source code
   - Connect your GitHub repository
   - Set build settings: Use `apprunner.yaml`
   - Add environment variables for API keys
   - Deploy

3. **Deploy Frontend to Amplify:**
   - Go to AWS Console → Amplify
   - Connect your GitHub repository  
   - Set build settings for Next.js
   - Add environment variable: `NEXT_PUBLIC_API_URL` = your App Runner URL
   - Deploy

### **Option 2: AWS ECS with Fargate (Production-Ready)**

Best for production with full control and scalability.

#### Steps:
1. **Update Configuration:**
```bash
# Edit deploy-aws.sh - replace YOUR_ACCOUNT_ID with your actual AWS Account ID
sed -i 's/YOUR_ACCOUNT_ID/123456789012/g' deploy-aws.sh
```

2. **Store API Keys in Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name "clinical-trials/openai-api-key" \
  --secret-string "your-openai-api-key"

aws secretsmanager create-secret \
  --name "clinical-trials/anthropic-api-key" \
  --secret-string "your-anthropic-api-key"
```

3. **Create IAM Roles:**
```bash
# Create execution role for ECS tasks
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# Attach required policies
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

4. **Create VPC and Security Groups:**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create subnets, security groups, etc.
# (Use AWS Console for easier setup)
```

5. **Deploy:**
```bash
./deploy-aws.sh
```

### **Option 3: Docker Compose (Local Testing)**

Test your containerized application locally:

```bash
# Create .env file with your API keys
echo "OPENAI_API_KEY=your-key" > .env
echo "ANTHROPIC_API_KEY=your-key" >> .env

# Start the application
docker-compose up --build
```

Access at: http://localhost:3000

## 💡 **Recommended Approach for Your Credits**

**Start with Option 1 (App Runner + Amplify):**
- ✅ Easiest to set up
- ✅ Handles all your AI dependencies
- ✅ Auto-scaling
- ✅ Cost-effective
- ✅ Perfect for demos and development

**Upgrade to Option 2 (ECS) later if needed:**
- More control
- Better for production
- More complex setup

## 🔧 **Environment Variables Required**

**Backend:**
- `OPENAI_API_KEY` (secret)
- `ANTHROPIC_API_KEY` (secret)  
- `CLINICAL_TRIALS_API_URL=https://clinicaltrials.gov/api/v2`
- `ENABLE_CLAUDE_PROVIDER=true`
- `ENABLE_OPENAI_PROVIDER=true`
- `ENABLE_QA_SYSTEM=true`
- `MAX_EXTRACTION_RETRIES=3`
- `REQUEST_TIMEOUT_MS=30000`

**Frontend:**
- `NEXT_PUBLIC_API_URL` (your backend URL)
- `OPENAI_API_KEY` (for client-side if needed)
- `ANTHROPIC_API_KEY` (for client-side if needed)

## 💰 **Cost Estimation**

**App Runner + Amplify:**
- App Runner: ~$25-50/month
- Amplify: ~$5-15/month
- Total: ~$30-65/month

**ECS Fargate:**
- Fargate: ~$30-70/month
- ALB: ~$20/month
- Total: ~$50-90/month

Both options are well within typical AWS credit limits!

## 🚀 **Next Steps**

1. Choose your deployment option
2. Set up AWS Secrets Manager with your API keys
3. Deploy using the chosen method
4. Test your application
5. Monitor with CloudWatch

Your Clinical Trials Matcher will be running with all advanced AI features intact!