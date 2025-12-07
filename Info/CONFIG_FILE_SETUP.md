# Configuration File Setup Guide

## Overview

The application uses a **`secrets_config.json`** file for all configuration instead of environment variables. This provides a single, easy-to-manage configuration file for both AWS Secrets Manager settings and local development credentials.

## Quick Start

### 1. Create Configuration File

Copy the template to create your configuration:

```bash
cd life_game
cp secrets_config.json.template secrets_config.json
```

### 2. Configure for Your Environment

Edit `life_game/secrets_config.json`:

#### Production (AWS Secrets Manager)

```json
{
  "use_aws_secrets": true,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/llm-api-keys",
  "local_development": {
    "openai_api_key": "",
    "anthropic_api_key": "",
    "llm_provider": "openai"
  }
}
```

#### Local Development (No AWS)

```json
{
  "use_aws_secrets": false,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/llm-api-keys",
  "local_development": {
    "openai_api_key": "sk-your-openai-key-here",
    "anthropic_api_key": "",
    "llm_provider": "openai"
  }
}
```

### 3. Run the Application

```bash
cd life_game
python app.py
```

No environment variables needed! 🎉

## Configuration Options

### `use_aws_secrets` (boolean)

- `true`: Retrieve API keys from AWS Secrets Manager
- `false`: Use `local_development` credentials from this config file

**Default**: `true`

### `aws_region` (string)

The AWS region where your secret is stored.

**Common values**:
- `us-east-1`
- `us-west-2`
- `eu-west-1`
- `ap-southeast-1`

**Default**: `us-east-1`

### `aws_secret_name` (string)

The name/path of your secret in AWS Secrets Manager.

**Default**: `life-game/llm-api-keys`

**Examples**:
- `life-game/llm-api-keys` (single environment)
- `life-game/dev/llm-api-keys` (development)
- `life-game/prod/llm-api-keys` (production)

### `local_development` (object)

Credentials used when `use_aws_secrets` is `false`.

**Fields**:
- `openai_api_key`: Your OpenAI API key (starts with `sk-`)
- `anthropic_api_key`: Your Anthropic API key (starts with `sk-ant-`)
- `llm_provider`: Which provider to use (`"openai"` or `"anthropic"`)

## Setup Scenarios

### Scenario 1: Production with AWS

1. **Create AWS secret** (see [AWS_SETUP.md](AWS_SETUP.md))
2. **Configure secrets_config.json**:
   ```json
   {
     "use_aws_secrets": true,
     "aws_region": "us-east-1",
     "aws_secret_name": "life-game/llm-api-keys",
     "local_development": {
       "openai_api_key": "",
       "anthropic_api_key": "",
       "llm_provider": "openai"
     }
   }
   ```
3. **Configure AWS credentials** (IAM role or AWS CLI)
4. **Run**: `python app.py`

### Scenario 2: Local Development (No AWS)

1. **Get API key** from OpenAI or Anthropic
2. **Configure secrets_config.json**:
   ```json
   {
     "use_aws_secrets": false,
     "aws_region": "us-east-1",
     "aws_secret_name": "life-game/llm-api-keys",
     "local_development": {
       "openai_api_key": "sk-proj-abc123...",
       "anthropic_api_key": "",
       "llm_provider": "openai"
     }
   }
   ```
3. **Run**: `python app.py`

### Scenario 3: Multiple Environments

Use different config files for each environment:

```bash
# Development
life_game/secrets_config.dev.json

# Staging
life_game/secrets_config.staging.json

# Production
life_game/secrets_config.prod.json
```

Then copy the appropriate one:
```bash
cp secrets_config.prod.json secrets_config.json
```

### Scenario 4: Team Development

1. **Never commit** `secrets_config.json` (it's in `.gitignore`)
2. **Commit** `secrets_config.json.template` with blank values
3. **Share** the template with your team
4. Each developer creates their own `secrets_config.json`

## Security Best Practices

### ✅ DO

- Keep `secrets_config.json` in `.gitignore`
- Use AWS Secrets Manager in production
- Set appropriate file permissions: `chmod 600 secrets_config.json`
- Use different secrets for dev/staging/prod
- Regularly rotate API keys

### ❌ DON'T

- Don't commit `secrets_config.json` to git
- Don't share your `secrets_config.json` file
- Don't use production keys in development
- Don't store secrets in public repositories
- Don't use the same API keys across environments

## File Permissions

Recommended file permissions for `secrets_config.json`:

```bash
chmod 600 life_game/secrets_config.json
```

This ensures only the owner can read/write the file.

## Troubleshooting

### "secrets_config.json not found"

The application will use default values (AWS Secrets Manager enabled).

**Solution**: Create the file from template:
```bash
cp secrets_config.json.template secrets_config.json
```

### "Invalid JSON in secrets_config.json"

**Error**: JSON syntax error in config file

**Solution**: Validate your JSON:
```bash
python -m json.tool secrets_config.json
```

Common issues:
- Missing commas between fields
- Trailing commas (not allowed in JSON)
- Unquoted keys or values
- Single quotes instead of double quotes

### API key not working

1. Check `use_aws_secrets` setting
2. If `false`, verify `local_development.openai_api_key` is set
3. If `true`, check AWS configuration (see [AWS_SETUP.md](AWS_SETUP.md))
4. Verify the API key is valid and has credits

### AWS connection fails

If `use_aws_secrets: true` but AWS is unavailable:

**Quick fix**: Switch to local mode:
```json
{
  "use_aws_secrets": false,
  "local_development": {
    "openai_api_key": "sk-your-backup-key",
    "llm_provider": "openai"
  }
}
```

## Migration from Environment Variables

If you previously used environment variables:

**Before** (environment variables):
```bash
export USE_AWS_SECRETS=true
export AWS_REGION=us-west-2
export AWS_SECRET_NAME=my-secret
export OPENAI_API_KEY=sk-123
```

**After** (secrets_config.json):
```json
{
  "use_aws_secrets": true,
  "aws_region": "us-west-2",
  "aws_secret_name": "my-secret",
  "local_development": {
    "openai_api_key": "sk-123",
    "llm_provider": "openai"
  }
}
```

No environment variables needed anymore! ✨

## Config File Location

The application looks for the config file at:
```
life_game/secrets_config.json
```

This path is relative to the `life_game` directory.

## Default Values

If `secrets_config.json` is missing, these defaults are used:

```json
{
  "use_aws_secrets": true,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/llm-api-keys",
  "local_development": {
    "openai_api_key": "",
    "anthropic_api_key": "",
    "llm_provider": "openai"
  }
}
```

## Example Configurations

### OpenAI Only (Local)

```json
{
  "use_aws_secrets": false,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/llm-api-keys",
  "local_development": {
    "openai_api_key": "sk-proj-...",
    "anthropic_api_key": "",
    "llm_provider": "openai"
  }
}
```

### Anthropic Only (Local)

```json
{
  "use_aws_secrets": false,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/llm-api-keys",
  "local_development": {
    "openai_api_key": "",
    "anthropic_api_key": "sk-ant-...",
    "llm_provider": "anthropic"
  }
}
```

### Both Providers (Local)

```json
{
  "use_aws_secrets": false,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/llm-api-keys",
  "local_development": {
    "openai_api_key": "sk-proj-...",
    "anthropic_api_key": "sk-ant-...",
    "llm_provider": "openai"
  }
}
```

Switch providers by changing `llm_provider` to `"anthropic"`.

### Production (AWS Secrets Manager)

```json
{
  "use_aws_secrets": true,
  "aws_region": "us-east-1",
  "aws_secret_name": "life-game/prod/llm-api-keys",
  "local_development": {
    "openai_api_key": "",
    "anthropic_api_key": "",
    "llm_provider": "openai"
  }
}
```

`local_development` values are ignored when `use_aws_secrets` is `true`.

## Testing Your Configuration

Test that your configuration works:

```bash
cd life_game
python -c "from config import config; print('OpenAI Key:', config.OPENAI_API_KEY[:10] + '...' if config.OPENAI_API_KEY else 'Not set')"
```

Expected output:
```
OpenAI Key: sk-proj-ab...
```

Or for AWS mode:
```
OpenAI Key: sk-...
```

## Summary

- ✅ **One file** for all configuration
- ✅ **No environment variables** needed
- ✅ **Easy switching** between AWS and local mode
- ✅ **Secure** (file is in .gitignore)
- ✅ **Flexible** for multiple environments
- ✅ **Simple** JSON format

For AWS-specific setup, see [AWS_SETUP.md](AWS_SETUP.md).
