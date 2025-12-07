# Chat Feature Setup Guide

## Overview
The game now includes an AI-powered chat feature where players can interact with NPCs at each location:
- **University**: Chat with a Professor
- **Job Office**: Chat with a Clerk
- **Workplace**: Chat with your Boss
- **Shop**: Chat with a Shopkeeper

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- openai (for OpenAI/ChatGPT integration)
- anthropic (for Claude integration)
- boto3 (AWS SDK for Secrets Manager)
- pytest (for running tests)

### 2. Configure LLM API Keys

**IMPORTANT**: The application uses a `secrets_config.json` file for all configuration.

#### Step 1: Create Configuration File

```bash
cd life_game
cp secrets_config.json.template secrets_config.json
```

#### Step 2: Choose Your Setup

**Option A: Using AWS Secrets Manager (Production)**

Edit `secrets_config.json`:
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

Then set up AWS Secrets Manager (see [AWS_SETUP.md](AWS_SETUP.md))

**Option B: Local Development (No AWS)**

Edit `secrets_config.json`:
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

Get your API key from:
- OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Anthropic: [console.anthropic.com](https://console.anthropic.com/)

For detailed configuration options, see [CONFIG_FILE_SETUP.md](CONFIG_FILE_SETUP.md)

### 3. Run the Game

```bash
cd life_game
python app.py
```

The game will be available at `http://localhost:5001`

## How to Use the Chat Feature

1. Log in to the game
2. Click on any location (University, Job Office, Workplace, or Shop)
3. In the modal popup, you'll see two tabs:
   - **Action**: Perform the location's main action (study, find job, work, shop)
   - **Chat**: Talk to the NPC at that location

4. Click the "Chat" tab to start a conversation
5. Type your message and press Enter or click "Send"
6. The NPC will respond based on their role and your current game state

## NPC Personalities

- **Professor** (University): Encouraging and knowledgeable about education
- **Clerk** (Job Office): Professional and helpful with job placement
- **Boss** (Workplace): Professional supervisor who manages your work
- **Shopkeeper** (Shop): Friendly and enthusiastic about products

Each NPC is aware of your current game state (money, qualification, job, etc.) and will provide contextually relevant responses.

## Model Configuration

You can change the specific model used by editing `life_game/config.py`:

```python
# For OpenAI
OPENAI_MODEL = 'gpt-4'  # or 'gpt-3.5-turbo' for a cheaper option

# For Anthropic
ANTHROPIC_MODEL = 'claude-3-5-sonnet-20241022'
```

## Cost Considerations

- API calls to LLM providers cost money
- OpenAI GPT-3.5-turbo is cheaper than GPT-4
- Consider setting usage limits in your API provider's dashboard
- Each chat message makes one API call

## Troubleshooting

**Error: "API key not configured"**
- Make sure you've set the API key in environment variables or config.py
- Restart the Flask app after setting environment variables

**Error: "Library not installed"**
- Run `pip install -r requirements.txt`

**Chat not responding**
- Check your API key is valid
- Check your internet connection
- Look at the Flask console for error messages
- Verify you have API credits remaining in your provider account
