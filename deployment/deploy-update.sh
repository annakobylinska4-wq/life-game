#!/bin/bash
set -e

# Update deployment script for Life Game
# Run this when you make code changes and want to deploy updates
# Works from local terminal (VS Code) or AWS CloudShell

export AWS_PAGER="" #to surpress pager display

echo "🔄 Updating Life Game deployment..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Navigate to the life_game directory (parent of deployment)
APP_DIR="$(dirname "$SCRIPT_DIR")"

# Load deployment configuration
source "$SCRIPT_DIR/deploy-config.sh"

echo "📁 Working directory: $APP_DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS CLI is not configured. Run 'aws configure' first."
    exit 1
fi

# Configuration
export AWS_REGION=${AWS_REGION:-eu-north-1}
export APP_NAME=life-game
export ECR_REPO_NAME=life-game
export S3_BUCKET_NAME=${APP_NAME}-data-$(echo $AWS_REGION | tr -d '-')

# Get AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region $AWS_REGION)

echo "📍 Region: $AWS_REGION"
echo "🔢 Account ID: $AWS_ACCOUNT_ID"
echo "🪣 S3 Bucket: $S3_BUCKET_NAME"

# Step 1: Build new Docker image
echo "🐳 Building Docker image..."
if [ -n "$DOCKER_PLATFORM" ]; then
    echo "   Platform: $DOCKER_PLATFORM"
    docker build --platform $DOCKER_PLATFORM -t $ECR_REPO_NAME "$APP_DIR"
else
    docker build -t $ECR_REPO_NAME "$APP_DIR"
fi

# Step 2: Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Tag and push
echo "🏷️  Tagging image..."
docker tag ${ECR_REPO_NAME}:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO_NAME}:latest

echo "⬆️  Pushing to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO_NAME}:latest

# Step 3b: Ensure S3 bucket exists and IAM policy is set
echo "🪣 Ensuring S3 bucket and IAM policy..."
if [ "$AWS_REGION" = "us-east-1" ]; then
    aws s3api create-bucket \
        --bucket $S3_BUCKET_NAME \
        --region $AWS_REGION 2>/dev/null || true
else
    aws s3api create-bucket \
        --bucket $S3_BUCKET_NAME \
        --region $AWS_REGION \
        --create-bucket-configuration LocationConstraint=$AWS_REGION 2>/dev/null || true
fi

# Ensure S3 IAM policy is attached
cat > /tmp/s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::${S3_BUCKET_NAME}",
      "arn:aws:s3:::${S3_BUCKET_NAME}/*"
    ]
  }]
}
EOF

aws iam put-role-policy \
    --role-name ecsTaskRole \
    --policy-name S3GameDataAccess \
    --policy-document file:///tmp/s3-policy.json 2>/dev/null || echo "S3 IAM policy update skipped"

# Step 4: Update task definition
echo "📋 Registering new task definition..."
cat > /tmp/task-definition.json <<EOF
{
  "family": "$APP_NAME",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskRole",
  "containerDefinitions": [{
    "name": "$APP_NAME",
    "image": "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest",
    "portMappings": [{
      "containerPort": 5001,
      "protocol": "tcp"
    }],
    "essential": true,
    "environment": [
      {"name": "S3_BUCKET_NAME", "value": "${S3_BUCKET_NAME}"},
      {"name": "AWS_REGION", "value": "${AWS_REGION}"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/$APP_NAME",
        "awslogs-region": "$AWS_REGION",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
EOF

aws ecs register-task-definition --cli-input-json file:///tmp/task-definition.json

# Step 5: Update ECS service
echo "🚀 Updating ECS service with new image..."
aws ecs update-service \
    --cluster ${APP_NAME}-cluster \
    --service ${APP_NAME}-service \
    --task-definition $APP_NAME \
    --force-new-deployment \
    --region $AWS_REGION

echo ""
echo "✅ Update initiated!"
echo ""
echo "⏳ The service will gradually replace old tasks with new ones (takes 2-3 minutes)"
echo ""
echo "📊 Monitor deployment:"
echo "   aws ecs describe-services --cluster ${APP_NAME}-cluster --services ${APP_NAME}-service --region $AWS_REGION"
echo ""
echo "📝 View logs:"
echo "   aws logs tail /ecs/$APP_NAME --follow --region $AWS_REGION"
