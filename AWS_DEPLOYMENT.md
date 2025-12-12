# AWS Fargate Deployment Guide

This guide walks you through deploying the Life Game application to AWS Fargate.

## Prerequisites

1. AWS CLI installed and configured
2. Docker installed locally
3. AWS account with appropriate permissions (ECS, ECR, VPC, IAM)

## Step 1: Test Docker Locally

```bash
# Build the image
docker build -t life-game .

# Test locally
docker run -p 5001:5001 life-game

# Or use docker-compose
docker-compose up
```

Visit http://localhost:5001 to verify it works.

## Step 2: Create ECR Repository

```bash
# Set variables
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME=life-game

# Create ECR repository
aws ecr create-repository \
    --repository-name $ECR_REPO_NAME \
    --region $AWS_REGION
```

## Step 3: Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build image with tag
docker build -t life-game .

# Tag image for ECR
docker tag life-game:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
```

## Step 4: Create Secrets in AWS Secrets Manager

Your application already uses AWS Secrets Manager! Configure your secrets:

```bash
# Create the secret with your API keys
aws secretsmanager create-secret \
    --name life-game/llm-api-keys \
    --description "LLM API keys for Life Game" \
    --secret-string '{
        "openai_api_key": "sk-your-key-here",
        "anthropic_api_key": "sk-ant-your-key-here",
        "llm_provider": "openai"
    }' \
    --region $AWS_REGION
```

## Step 5: Create ECS Task Execution Role

```bash
# Create trust policy
cat > task-execution-role-trust-policy.json <<EOF
{
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
}
EOF

# Create role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file://task-execution-role-trust-policy.json

# Attach managed policy
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

## Step 6: Create ECS Task Role (for Secrets Manager access)

```bash
# Create task role trust policy
cat > task-role-trust-policy.json <<EOF
{
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
}
EOF

# Create task role
aws iam create-role \
    --role-name ecsTaskRole \
    --assume-role-policy-document file://task-role-trust-policy.json

# Create policy for Secrets Manager access
cat > secrets-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:life-game/*"
    }
  ]
}
EOF

# Attach policy to task role
aws iam put-role-policy \
    --role-name ecsTaskRole \
    --policy-name SecretsManagerAccess \
    --policy-document file://secrets-policy.json
```

## Step 7: Create ECS Task Definition

```bash
cat > task-definition.json <<EOF
{
  "family": "life-game",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "life-game",
      "image": "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest",
      "portMappings": [
        {
          "containerPort": 5001,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/life-game",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/life-game --region $AWS_REGION

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

## Step 8: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name life-game-cluster --region $AWS_REGION
```

## Step 9: Create Application Load Balancer (Optional but Recommended)

```bash
# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)

# Get subnets
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text)

# Create security group for ALB
ALB_SG=$(aws ec2 create-security-group \
    --group-name life-game-alb-sg \
    --description "Security group for Life Game ALB" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Create security group for ECS tasks
ECS_SG=$(aws ec2 create-security-group \
    --group-name life-game-ecs-sg \
    --description "Security group for Life Game ECS tasks" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

# Allow traffic from ALB to ECS
aws ec2 authorize-security-group-ingress \
    --group-id $ECS_SG \
    --protocol tcp \
    --port 5001 \
    --source-group $ALB_SG

# Create ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name life-game-alb \
    --subnets $SUBNET_IDS \
    --security-groups $ALB_SG \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Create target group
TG_ARN=$(aws elbv2 create-target-group \
    --name life-game-tg \
    --protocol HTTP \
    --port 5001 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path / \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

## Step 10: Create ECS Service

```bash
# Get subnet IDs as comma-separated
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text | tr '\t' ',')

# Create service with ALB
aws ecs create-service \
    --cluster life-game-cluster \
    --service-name life-game-service \
    --task-definition life-game \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TG_ARN,containerName=life-game,containerPort=5001"
```

## Step 11: Get Application URL

```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].DNSName' \
    --output text
```

Visit the URL in your browser!

## Updating the Application

When you make code changes:

```bash
# Rebuild and push
docker build -t life-game .
docker tag life-game:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Update service to use new image
aws ecs update-service \
    --cluster life-game-cluster \
    --service life-game-service \
    --force-new-deployment
```

## Cost Optimization

- **Fargate Spot**: Use Fargate Spot for 70% cost savings (not suitable for production)
- **Right-size resources**: Start with 256 CPU / 512 MB memory, adjust as needed
- **Auto-scaling**: Configure based on CPU/memory utilization
- **ALB**: Consider using API Gateway + Lambda for lower traffic

## Monitoring

```bash
# View logs
aws logs tail /ecs/life-game --follow

# Check service status
aws ecs describe-services \
    --cluster life-game-cluster \
    --services life-game-service
```

## Cleanup

```bash
# Delete service
aws ecs delete-service --cluster life-game-cluster --service life-game-service --force

# Delete cluster
aws ecs delete-cluster --cluster life-game-cluster

# Delete ALB and target group
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete ECR repository
aws ecr delete-repository --repository-name $ECR_REPO_NAME --force

# Delete log group
aws logs delete-log-group --log-group-name /ecs/life-game
```

## Troubleshooting

- **Container won't start**: Check CloudWatch logs
- **Can't access application**: Verify security group rules
- **Secrets not loading**: Check IAM task role has Secrets Manager permissions
- **502/503 errors**: Check health check settings in target group
