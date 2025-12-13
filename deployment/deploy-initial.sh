#!/bin/bash
set -e

# Initial deployment script for Life Game to AWS Fargate
# Run this ONCE to set up all infrastructure

echo "🚀 Starting initial deployment to AWS Fargate..."

# Load deployment configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/deploy-config.sh"

# Configuration
export AWS_REGION=${AWS_REGION:-eu-north-1}
export APP_NAME=life-game
export ECR_REPO_NAME=life-game

# Get AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "📍 Region: $AWS_REGION"
echo "🔢 Account ID: $AWS_ACCOUNT_ID"

# Step 1: Create ECR Repository
echo "📦 Creating ECR repository..."
aws ecr create-repository \
    --repository-name $ECR_REPO_NAME \
    --region $AWS_REGION 2>/dev/null || echo "ECR repository already exists"

# Step 2: Build and push Docker image
echo "🐳 Building Docker image..."
if [ -n "$DOCKER_PLATFORM" ]; then
    echo "   Platform: $DOCKER_PLATFORM"
    docker build --platform $DOCKER_PLATFORM -t $ECR_REPO_NAME .
else
    docker build -t $ECR_REPO_NAME .
fi

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "🏷️  Tagging image..."
docker tag $ECR_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

echo "⬆️  Pushing to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Step 3: Create IAM Roles
echo "👤 Creating IAM roles..."

cat > /tmp/task-execution-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file:///tmp/task-execution-trust-policy.json 2>/dev/null || echo "ecsTaskExecutionRole already exists"

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>/dev/null || echo "Policy already attached"

aws iam create-role \
    --role-name ecsTaskRole \
    --assume-role-policy-document file:///tmp/task-execution-trust-policy.json 2>/dev/null || echo "ecsTaskRole already exists"

cat > /tmp/secrets-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["secretsmanager:GetSecretValue"],
    "Resource": "arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT_ID}:secret:prod/MrJones/*"
  }]
}
EOF

aws iam put-role-policy \
    --role-name ecsTaskRole \
    --policy-name SecretsManagerAccess \
    --policy-document file:///tmp/secrets-policy.json

echo "⏳ Waiting 10 seconds for IAM roles to propagate..."
sleep 10

# Step 4: Create ECS Cluster
echo "🏗️  Creating ECS cluster..."
aws ecs create-cluster --cluster-name ${APP_NAME}-cluster --region $AWS_REGION 2>/dev/null || echo "Cluster already exists"

# Step 5: Create CloudWatch log group
echo "📝 Creating CloudWatch log group..."
aws logs create-log-group --log-group-name /ecs/$APP_NAME --region $AWS_REGION 2>/dev/null || echo "Log group already exists"

# Step 6: Register task definition
echo "📋 Registering task definition..."
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

# Step 7: Set up networking
echo "🌐 Setting up networking..."
export VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $AWS_REGION)
export SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $AWS_REGION)

echo "🔒 Creating security groups..."
export ALB_SG=$(aws ec2 create-security-group \
    --group-name ${APP_NAME}-alb-sg \
    --description "Security group for Life Game ALB" \
    --vpc-id $VPC_ID \
    --region $AWS_REGION \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups --filters "Name=group-name,Values=${APP_NAME}-alb-sg" --query "SecurityGroups[0].GroupId" --output text --region $AWS_REGION)

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || echo "ALB ingress rule already exists"

export ECS_SG=$(aws ec2 create-security-group \
    --group-name ${APP_NAME}-ecs-sg \
    --description "Security group for Life Game ECS" \
    --vpc-id $VPC_ID \
    --region $AWS_REGION \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups --filters "Name=group-name,Values=${APP_NAME}-ecs-sg" --query "SecurityGroups[0].GroupId" --output text --region $AWS_REGION)

aws ec2 authorize-security-group-ingress \
    --group-id $ECS_SG \
    --protocol tcp \
    --port 5001 \
    --source-group $ALB_SG \
    --region $AWS_REGION 2>/dev/null || echo "ECS ingress rule already exists"

# Step 8: Create Application Load Balancer
echo "⚖️  Creating Application Load Balancer..."
export ALB_ARN=$(aws elbv2 create-load-balancer \
    --name ${APP_NAME}-alb \
    --subnets $SUBNET_IDS \
    --security-groups $ALB_SG \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text 2>/dev/null || \
    aws elbv2 describe-load-balancers --names ${APP_NAME}-alb --query "LoadBalancers[0].LoadBalancerArn" --output text --region $AWS_REGION)

# Step 9: Create target group
echo "🎯 Creating target group..."
export TG_ARN=$(aws elbv2 create-target-group \
    --name ${APP_NAME}-tg \
    --protocol HTTP \
    --port 5001 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path / \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null || \
    aws elbv2 describe-target-groups --names ${APP_NAME}-tg --query "TargetGroups[0].TargetGroupArn" --output text --region $AWS_REGION)

# Step 10: Create listener
echo "👂 Creating listener..."
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN \
    --region $AWS_REGION 2>/dev/null || echo "Listener already exists"

# Step 11: Create ECS Service
echo "🚢 Creating ECS service..."
export SUBNETS_CSV=$(echo $SUBNET_IDS | tr ' ' ',')

aws ecs create-service \
    --cluster ${APP_NAME}-cluster \
    --service-name ${APP_NAME}-service \
    --task-definition $APP_NAME \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS_CSV],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TG_ARN,containerName=$APP_NAME,containerPort=5001" \
    --region $AWS_REGION 2>/dev/null || echo "Service already exists - use deploy-update.sh to update"

# Step 12: Get URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌍 Your application URL:"
aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].DNSName' \
    --output text

echo ""
echo "⏳ Note: It may take 2-3 minutes for the service to start"
echo ""
echo "📊 Monitor logs with:"
echo "   aws logs tail /ecs/$APP_NAME --follow --region $AWS_REGION"
echo ""
echo "🔄 To update your app later, use: ./deploy-update.sh"