# AWS Secrets Manager Setup Guide

## Overview

The application now retrieves LLM API keys from AWS Secrets Manager instead of environment variables. This provides better security and centralized secret management.

## Prerequisites

1. AWS Account with access to AWS Secrets Manager
2. AWS CLI configured with appropriate credentials
3. IAM permissions for Secrets Manager operations

## Step 1: Create a Secret in AWS Secrets Manager

### Option A: Using AWS Console

1. Log in to AWS Console
2. Navigate to **AWS Secrets Manager**
3. Click **Store a new secret**
4. Select **Other type of secret**
5. Under **Key/value pairs**, add the following:

   ```json
   {
     "openai_api_key": "sk-your-openai-key-here",
     "anthropic_api_key": "sk-ant-your-anthropic-key-here",
     "llm_provider": "openai"
   }
   ```

   **Note**: You can include just one API key if you only use one provider.

6. Click **Next**
7. **Secret name**: Enter `life-game/llm-api-keys` (or your custom name)
8. **Description**: (Optional) "LLM API keys for Life Game application"
9. Click **Next**
10. **Configure automatic rotation**: Disable (unless you want automatic key rotation)
11. Click **Next** and then **Store**

### Option B: Using AWS CLI

```bash
# Create the secret with JSON content
aws secretsmanager create-secret \
    --name life-game/llm-api-keys \
    --description "LLM API keys for Life Game" \
    --secret-string '{
        "openai_api_key": "sk-your-openai-key-here",
        "anthropic_api_key": "sk-ant-your-anthropic-key-here",
        "llm_provider": "openai"
    }' \
    --region us-east-1
```

### Update an Existing Secret

```bash
aws secretsmanager update-secret \
    --secret-id life-game/llm-api-keys \
    --secret-string '{
        "openai_api_key": "sk-your-new-openai-key",
        "anthropic_api_key": "sk-ant-your-new-anthropic-key",
        "llm_provider": "anthropic"
    }' \
    --region us-east-1
```

## Step 2: Configure IAM Permissions

Your application needs IAM permissions to read from Secrets Manager. Attach this policy to your IAM role or user:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:YOUR-ACCOUNT-ID:secret:life-game/llm-api-keys-*"
        }
    ]
}
```

Replace `YOUR-ACCOUNT-ID` with your AWS account ID.

## Step 3: Configure AWS Credentials

The application uses boto3 to access AWS. Configure credentials using one of these methods:

### Option A: AWS CLI Configuration

```bash
aws configure
```

This creates `~/.aws/credentials` and `~/.aws/config`

### Option B: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

### Option C: IAM Role (Recommended for EC2/ECS/Lambda)

When running on AWS services, use an IAM role instead of credentials.

## Step 4: Configure Application

### Environment Variables

```bash
# Enable AWS Secrets Manager (default: true)
export USE_AWS_SECRETS=true

# AWS region (default: us-east-1)
export AWS_REGION=us-east-1

# Custom secret name (default: life-game/llm-api-keys)
export AWS_SECRET_NAME=life-game/llm-api-keys
```

### Configuration File

Alternatively, edit `life_game/config.py`:

```python
class Config:
    AWS_REGION = 'us-east-1'
    AWS_SECRET_NAME = 'life-game/llm-api-keys'
    USE_AWS_SECRETS = True
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs boto3 (AWS SDK for Python).

## Step 6: Run the Application

```bash
cd life_game
python app.py
```

The application will:
1. Connect to AWS Secrets Manager
2. Retrieve the secret `life-game/llm-api-keys`
3. Extract API keys and provider configuration
4. Use them for LLM chat functionality

## Local Development (Without AWS)

For local development, you can disable AWS Secrets Manager and use environment variables:

```bash
# Disable AWS Secrets Manager
export USE_AWS_SECRETS=false

# Use environment variables instead
export OPENAI_API_KEY=sk-your-key
export LLM_PROVIDER=openai

# Run the application
cd life_game
python app.py
```

## Running Tests

Tests work with both AWS Secrets Manager and environment variables:

### With AWS Secrets Manager

```bash
export USE_AWS_SECRETS=true
export AWS_REGION=us-east-1
python -m pytest tests/ -v
```

### Without AWS Secrets Manager

```bash
export USE_AWS_SECRETS=false
export OPENAI_API_KEY=sk-your-key
python -m pytest tests/ -v
```

## Secret Format Options

### Full Configuration (Recommended)

```json
{
    "openai_api_key": "sk-...",
    "anthropic_api_key": "sk-ant-...",
    "llm_provider": "openai"
}
```

### Single Provider

```json
{
    "openai_api_key": "sk-...",
    "llm_provider": "openai"
}
```

Or:

```json
{
    "anthropic_api_key": "sk-ant-...",
    "llm_provider": "anthropic"
}
```

### Simple String (Single API Key)

If you store just a string (not JSON), the application will use `LLM_PROVIDER` env var to determine which provider it's for:

```
sk-your-api-key-here
```

## Troubleshooting

### Error: "Secret not found in AWS Secrets Manager"

- Verify the secret name matches: `life-game/llm-api-keys`
- Check AWS region configuration
- Verify the secret exists: `aws secretsmanager list-secrets`

### Error: "Access Denied"

- Check IAM permissions
- Verify your AWS credentials are configured
- Ensure the IAM policy allows `secretsmanager:GetSecretValue`

### Error: "Could not load from AWS Secrets Manager"

- Check internet connectivity
- Verify AWS credentials are valid
- Check boto3 is installed: `pip install boto3`
- Application will fall back to environment variables

### Application uses wrong API key

- Check the `llm_provider` value in your secret
- Verify the secret contains the correct keys
- Try reloading: `config.reload_secrets()`

## Security Best Practices

1. **Use IAM Roles** when running on AWS (EC2, ECS, Lambda, etc.)
2. **Rotate secrets regularly** using AWS Secrets Manager rotation
3. **Limit IAM permissions** to only the specific secret needed
4. **Use different secrets** for dev/staging/production environments
5. **Enable CloudTrail** to audit secret access
6. **Never commit secrets** to version control

## Cost Considerations

- AWS Secrets Manager costs $0.40 per secret per month
- $0.05 per 10,000 API calls
- For this application, costs should be minimal (< $1/month)

## Multiple Environments

Use different secret names for different environments:

```bash
# Development
export AWS_SECRET_NAME=life-game/dev/llm-api-keys

# Staging
export AWS_SECRET_NAME=life-game/staging/llm-api-keys

# Production
export AWS_SECRET_NAME=life-game/prod/llm-api-keys
```

## Monitoring

Monitor secret usage in CloudWatch:
- Number of GetSecretValue calls
- Failed access attempts
- Secret rotation status

Set up CloudWatch alarms for suspicious activity.
