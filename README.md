# Life Game with a LLM twist

A turn-based life simulation game where you navigate through life decisions, manage resources, and build your career. 
Initial functionality allows the user to influence the game by chatting with other game personas (such as a shopkeeper, estate agent etc.) 
through OpenAI function calling.
Built with FastAPI and vanilla JavaScript.
Game can be accessed at coolgaming.co.uk

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

## Running the Game

### Option 1: Local Development

Run the application directly with uvicorn:

```bash
python3 -m uvicorn life-game.app:app --host 0.0.0.0 --port 5001 --reload
```

Then open your browser and navigate to:
```
http://localhost:5001
```

### Option 2: Docker (Local Testing)

1. Set build target to local in `deployment/deploy-config.sh`:
   ```bash
   BUILD_TARGET="local"
   ```

2. Build and run the container:
   ```bash
   cd life_game
   docker build -t life-game .
   docker run -p 5001:5001 life-game
   ```

3. Access at `http://localhost:5001`

### Option 3: AWS Deployment

The game is deployed on AWS Fargate and accessible at:
```
http://life-game-alb-1075655009.eu-north-1.elb.amazonaws.com
```

To deploy updates:

1. Ensure build target is set to AWS in `deployment/deploy-config.sh`:
   ```bash
   BUILD_TARGET="aws"
   ```

2. Run the deployment script:
   ```bash
   cd life_game/deployment
   ./deploy-update.sh
   ```

3. Wait 2-3 minutes for the service to update.

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
