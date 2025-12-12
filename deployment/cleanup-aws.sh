#!/bin/bash
set -e

# Cleanup script to delete all AWS resources
# WARNING: This will delete everything!

echo "⚠️  WARNING: This will delete ALL AWS resources for Life Game"
echo ""
read -p "Are you sure? Type 'yes' to continue: " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Configuration
export AWS_REGION=${AWS_REGION:-eu-north-1}
export APP_NAME=life-game
export ECR_REPO_NAME=life-game
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🗑️  Starting cleanup..."

# Step 1: Delete ECS Service
echo "Deleting ECS service..."
aws ecs update-service \
    --cluster ${APP_NAME}-cluster \
    --service ${APP_NAME}-service \
    --desired-count 0 \
    --region $AWS_REGION 2>/dev/null || echo "Service not found"

aws ecs delete-service \
    --cluster ${APP_NAME}-cluster \
    --service ${APP_NAME}-service \
    --force \
    --region $AWS_REGION 2>/dev/null || echo "Service already deleted"

echo "⏳ Waiting for service to drain..."
sleep 10

# Step 2: Delete ECS Cluster
echo "Deleting ECS cluster..."
aws ecs delete-cluster \
    --cluster ${APP_NAME}-cluster \
    --region $AWS_REGION 2>/dev/null || echo "Cluster already deleted"

# Step 3: Delete Load Balancer
echo "Deleting ALB..."
export ALB_ARN=$(aws elbv2 describe-load-balancers \
    --names ${APP_NAME}-alb \
    --query "LoadBalancers[0].LoadBalancerArn" \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ "$ALB_ARN" != "None" ] && [ -n "$ALB_ARN" ]; then
    aws elbv2 delete-load-balancer \
        --load-balancer-arn $ALB_ARN \
        --region $AWS_REGION
    echo "⏳ Waiting for ALB to delete..."
    sleep 30
fi

# Step 4: Delete Target Group
echo "Deleting target group..."
export TG_ARN=$(aws elbv2 describe-target-groups \
    --names ${APP_NAME}-tg \
    --query "TargetGroups[0].TargetGroupArn" \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ "$TG_ARN" != "None" ] && [ -n "$TG_ARN" ]; then
    aws elbv2 delete-target-group \
        --target-group-arn $TG_ARN \
        --region $AWS_REGION 2>/dev/null || echo "Target group already deleted"
fi

# Step 5: Delete Security Groups
echo "Deleting security groups..."
export VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query "Vpcs[0].VpcId" \
    --output text \
    --region $AWS_REGION)

export ECS_SG=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=${APP_NAME}-ecs-sg" \
    --query "SecurityGroups[0].GroupId" \
    --output text \
    --region $AWS_REGION 2>/dev/null)

export ALB_SG=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=${APP_NAME}-alb-sg" \
    --query "SecurityGroups[0].GroupId" \
    --output text \
    --region $AWS_REGION 2>/dev/null)

if [ "$ECS_SG" != "None" ] && [ -n "$ECS_SG" ]; then
    aws ec2 delete-security-group --group-id $ECS_SG --region $AWS_REGION 2>/dev/null || echo "ECS SG already deleted"
fi

if [ "$ALB_SG" != "None" ] && [ -n "$ALB_SG" ]; then
    aws ec2 delete-security-group --group-id $ALB_SG --region $AWS_REGION 2>/dev/null || echo "ALB SG already deleted"
fi

# Step 6: Delete ECR Repository
echo "Deleting ECR repository..."
aws ecr delete-repository \
    --repository-name $ECR_REPO_NAME \
    --force \
    --region $AWS_REGION 2>/dev/null || echo "ECR repository already deleted"

# Step 7: Delete CloudWatch Log Group
echo "Deleting CloudWatch logs..."
aws logs delete-log-group \
    --log-group-name /ecs/$APP_NAME \
    --region $AWS_REGION 2>/dev/null || echo "Log group already deleted"

# Note: We don't delete IAM roles or Secrets Manager secrets as they might be used by other apps

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "ℹ️  Note: IAM roles (ecsTaskExecutionRole, ecsTaskRole) and Secrets Manager secrets were NOT deleted"
echo "   Delete them manually if needed:"
echo "   - aws iam delete-role-policy --role-name ecsTaskRole --policy-name SecretsManagerAccess"
echo "   - aws iam detach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
echo "   - aws iam delete-role --role-name ecsTaskExecutionRole"
echo "   - aws iam delete-role --role-name ecsTaskRole"
echo "   - aws secretsmanager delete-secret --secret-id prod/MrJones/LLMOpenAI --force-delete-without-recovery"
