# Life Game - AWS Deployment Guide

This folder contains automated scripts to deploy the Life Game application to AWS Fargate.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI configured with credentials
- Access to AWS CloudShell (recommended) or local terminal with Docker installed

## Quick Start

### Option 1: Using AWS CloudShell (Recommended)

1. **Open AWS CloudShell**
   - Log into AWS Console
   - Click the CloudShell icon in the top-right corner
   - Wait for it to initialize

2. **Clone your repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME/deployment
   ```

3. **Make scripts executable**
   ```bash
   chmod +x *.sh
   ```

4. **Set your AWS region** (optional, defaults to eu-north-1)
   ```bash
   export AWS_REGION=eu-north-1
   ```

5. **Run initial deployment**
   ```bash
   ./deploy-initial.sh
   ```

6. **Get your application URL**
   - The script will output the URL at the end
   - Wait 2-3 minutes for the service to start
   - Visit the URL in your browser

### Option 2: Using Local Terminal

Same steps as above, but requires:
- Docker installed locally
- AWS CLI configured with `aws configure`

## Scripts Overview

### 📦 deploy-initial.sh
**Purpose:** First-time deployment - creates all AWS infrastructure

**What it does:**
- Creates ECR repository
- Builds and pushes Docker image
- Creates IAM roles (ecsTaskExecutionRole, ecsTaskRole)
- Creates ECS cluster
- Sets up networking (VPC, security groups)
- Creates Application Load Balancer
- Creates ECS Fargate service
- Outputs application URL

**When to use:** Run this **ONCE** when deploying for the first time

**Usage:**
```bash
./deploy-initial.sh
```

---

### 🔄 deploy-update.sh
**Purpose:** Deploy code changes to existing infrastructure

**What it does:**
- Builds new Docker image with your latest code
- Pushes to ECR
- Updates ECS task definition
- Triggers rolling deployment (zero downtime)

**When to use:** Every time you make code changes and want to deploy

**Usage:**
```bash
# Update your code locally, commit, and push to GitHub
git pull
./deploy-update.sh
```

---

### 🗑️ cleanup-aws.sh
**Purpose:** Delete all AWS resources

**What it does:**
- Deletes ECS service and cluster
- Deletes Application Load Balancer
- Deletes target group
- Deletes security groups
- Deletes ECR repository
- Deletes CloudWatch logs

**When to use:** When you want to tear down everything (saves costs)

**Usage:**
```bash
./cleanup-aws.sh
# Type 'yes' to confirm deletion
```

**Note:** IAM roles and Secrets Manager secrets are NOT deleted (they may be used by other apps)

---

## Before First Deployment

### 1. Create API Keys Secret in AWS Secrets Manager

Your application needs API keys stored in AWS Secrets Manager:

```bash
export AWS_REGION=eu-north-1

aws secretsmanager create-secret \
    --name prod/MrJones/LLMOpenAI \
    --description "LLM API keys for Life Game" \
    --secret-string '{
        "openai_api_key": "YOUR_ACTUAL_OPENAI_KEY_HERE",
        "anthropic_api_key": "",
        "llm_provider": "openai"
    }' \
    --region $AWS_REGION
```

**Important:** Replace `YOUR_ACTUAL_OPENAI_KEY_HERE` with your real OpenAI API key

### 2. Verify Configuration

Check your [config/secrets_config.json.example](../config/secrets_config.json.example):
- Make sure `use_aws_secrets` is `true`
- Verify `aws_region` matches your deployment region
- Verify `aws_secret_name` matches the secret you created

## Deployment Workflow

### Initial Deployment
```bash
# 1. Open AWS CloudShell
# 2. Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/deployment

# 3. Make executable
chmod +x *.sh

# 4. Deploy
./deploy-initial.sh

# 5. Get URL from output and visit in browser
```

### Making Updates
```bash
# 1. Make code changes locally and push to GitHub
git add .
git commit -m "Your changes"
git push

# 2. In AWS CloudShell, pull latest code
cd YOUR_REPO
git pull

# 3. Deploy update
cd deployment
./deploy-update.sh

# 4. Wait 2-3 minutes for rolling deployment
```

### Cleanup (Delete Everything)
```bash
cd YOUR_REPO/deployment
./cleanup-aws.sh
# Type 'yes' to confirm
```

## Monitoring & Troubleshooting

### View Application Logs
```bash
export AWS_REGION=eu-north-1
aws logs tail /ecs/life-game --follow --region $AWS_REGION
```

### Check Service Status
```bash
aws ecs describe-services \
    --cluster life-game-cluster \
    --services life-game-service \
    --region $AWS_REGION
```

### Check Running Tasks
```bash
aws ecs list-tasks \
    --cluster life-game-cluster \
    --region $AWS_REGION
```

### Common Issues

**Container won't start:**
- Check CloudWatch logs: `aws logs tail /ecs/life-game --follow`
- Verify Secrets Manager has the correct API keys
- Check IAM task role has permissions

**Can't access application:**
- Wait 2-3 minutes after deployment
- Verify security group rules allow port 80
- Check target group health: AWS Console → EC2 → Target Groups

**502/503 errors:**
- Application may be starting up (wait a few minutes)
- Check health check settings in target group
- Verify app is running on port 5001

**Authentication errors:**
- Verify Secrets Manager secret exists and has correct format
- Check IAM task role has `secretsmanager:GetSecretValue` permission

## Cost Estimate

Running this application on AWS Fargate costs approximately:

- **Fargate Task (256 CPU, 512 MB):** ~$10-15/month (if running 24/7)
- **Application Load Balancer:** ~$16-20/month
- **Data Transfer:** Varies based on usage
- **ECR Storage:** <$1/month
- **CloudWatch Logs:** <$5/month

**Total:** ~$30-40/month for 24/7 operation

**Cost Saving Tips:**
- Stop the service when not in use (set desired count to 0)
- Use Fargate Spot for 70% savings (less reliable)
- Consider using smaller instance sizes if sufficient

## Architecture

```
Internet → ALB (Port 80) → ECS Fargate (Port 5001) → Your App
                                ↓
                          AWS Secrets Manager (API Keys)
```

## Additional Resources

- [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) - Detailed manual deployment guide
- [AWS Fargate Docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [AWS CloudShell Docs](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html)

## Support

If you encounter issues:
1. Check CloudWatch logs
2. Review the troubleshooting section above
3. Consult AWS_DEPLOYMENT.md for detailed manual steps
