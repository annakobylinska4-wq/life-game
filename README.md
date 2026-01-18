# Life Game with an LLM twist
*** Game can be accessed at coolgaming.co.uk ***

A turn-based life simulation game where you navigate through life decisions, manage resources, and build your career. 
Initial functionality allows the user to influence the game by chatting with other game personas (such as a shopkeeper, estate agent etc.) 
through OpenAI function calling.
Built with FastAPI and vanilla JavaScript.


## Features

- User registration and authentication
- Turn-based gameplay with persistent game state
- Resource management: money, happiness, tiredness, hunger
- Job system with qualifications and wages
- Shop system for purchasing items
- AI-powered chat interactions (OpenAI/Anthropic)

## Requirements

- Python 3.8+
- Docker (for containerized deployment)

## Installation

1. Clone the repository and navigate to the project:
   ```bash
   cd life_game
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure data files exist with valid JSON:
   ```bash
   mkdir -p data
   echo '{}' > data/users.json
   echo '{}' > data/game_states.json
   ```

## Project Structure

```
life_game/
├── app.py              # FastAPI application
├── config/             # Configuration files
├── models/             # Game state models
├── actions/            # Game action handlers
├── chatbot/            # LLM integration
├── templates/          # HTML templates
├── static/             # CSS and JavaScript
├── data/               # User and game state data
├── deployment/         # AWS deployment scripts
│   ├── deploy-initial.sh   # First-time infrastructure setup
│   ├── deploy-update.sh    # Update existing deployment
│   └── deploy-config.sh    # Build configuration
├── Dockerfile
└── requirements.txt
```

## Configuration

- `config/config.py` - Main application configuration
- `config/secrets_config.json` - API keys (local development)
- `config/aws_secrets_config.json` - AWS Secrets Manager configuration
- `deployment/deploy-config.sh` - Docker build target (local/aws)
