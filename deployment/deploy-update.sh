#!/bin/bash
set -e

# Update deployment script for Life Game
# Run this when you make code changes and want to deploy updates

echo "🔄 Updating Life Game deployment..."

# Configuration
export AWS_REGION=${AWS_REGION:-eu-north-1}
export APP_NAME=life-game
export ECR_REPO_NAME=life-game

# Get AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "📍 Region: $AWS_REGION"
echo "🔢 Account ID: $AWS_ACCOUNT_ID"

# Step 1: Build new Docker image
echo "🐳 Building Docker image..."
docker build -t $ECR_REPO_NAME .

# Step 2: Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Tag and push
echo "🏷️  Tagging image..."
docker tag $ECR_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

echo "⬆️  Pushing to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

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
