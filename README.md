# Life Game with an LLM twist
**Live at: [coolgaming.co.uk](http://coolgaming.co.uk)**

A turn-based life simulation game where you navigate through life decisions, manage resources (money, happiness, tiredness, hunger), build your career through education, and interact with AI-powered NPCs. The game features LLM integration (OpenAI GPT-4o-mini or Anthropic Claude-3.5-Sonnet) for dynamic chat interactions using tool calling via Model Context Protocol (MCP).

Built with **FastAPI** backend and **vanilla JavaScript** frontend, deployed on AWS with S3 storage.

---

## ✨ Features

### Core Gameplay
- **Turn-based 24-hour day cycle** with real-time clock (starts at 6:00 AM)
- **Resource management**: Money, happiness (0-100), tiredness (0-100), hunger (0-100+)
- **Time-based actions**: Each action costs 3 hours (1h travel + 2h action)
- **Endgame conditions**: Burnout (exhausted + starving) or bankruptcy (money < £0)

### Progression Systems
- **Education ladder**: Middle school → High school → Vocational/Bachelor → Master → PhD
- **Job system**: 15+ jobs with wages £10-£150, unlocked by qualifications and appearance
- **Appearance system**: 5 look levels (Shabby → Very well groomed) based on clothing items
- **Housing ladder**: 6 flat tiers from homeless to luxury penthouse (£0-£200 rent/day)

### Locations & Activities
- **Home**: Rest to recover tiredness (benefits scale with flat tier)
- **Workplace**: Work 2-hour shifts to earn money (wage depends on job)
- **Shop**: Buy 15 food items to reduce hunger
- **John Lewis**: Purchase 12 clothing/furniture items to improve appearance
- **University**: Enroll in courses and attend lectures (opening hours: 6am-8pm)
- **Job Office**: Apply for jobs based on qualifications and look (opening hours: 6am-8pm)
- **Estate Agent**: Rent better flats for improved rest and happiness (opening hours: 6am-8pm)

### AI-Powered Interactions
- **LLM tool calling**: Chat with NPCs who can execute game actions on your behalf
- **6 unique NPC personalities**: Professor, job clerk, boss, grumpy shopkeeper, flatmate, sales assistant
- **Dual LLM support**: Switch between OpenAI (GPT-4o-mini) and Anthropic (Claude-3.5-Sonnet)
- **Model Context Protocol (MCP)**: 6 tools for NPCs (apply_for_job, study, work, buy_item, rest, buy_clothes)

### Technical Features
- **Cookie-based authentication** with signed session tokens
- **Persistent storage**: Dual-mode (AWS S3 or local filesystem) with automatic fallback
- **Structured logging**: Loguru with periodic S3 upload (every 60 seconds)
- **AWS Secrets Manager integration** for production API key management
- **Docker containerization** for consistent deployment

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- AWS account (optional, for S3 storage and secrets)

### Local Development Setup

1. **Clone and navigate to project**:
   ```bash
   git clone <repository-url>
   cd life-game
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** (create `config/secrets_config.json`):
   ```json
   {
     "OPENAI_API_KEY": "sk-...",
     "ANTHROPIC_API_KEY": "sk-ant-...",
     "SECRET_KEY": "your-secret-key-for-sessions"
   }
   ```

4. **Initialize local data storage**:
   ```bash
   mkdir -p data
   echo '{}' > data/users.json
   echo '{}' > data/game_states.json
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 5001 --reload
   ```

6. **Access the game**: Open [http://localhost:5001](http://localhost:5001)

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t life-game .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 5001:5001 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/config:/app/config \
     --name life-game \
     life-game
   ```

3. **Access the game**: Open [http://localhost:5001](http://localhost:5001)

---

## 📁 Project Structure

```
life-game/
├── app.py                      # FastAPI application entry point (145 lines)
├── schemas.py                  # Pydantic request/response models (40 lines)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker containerization config
├── docker-compose.yml          # Docker Compose setup
├── setup-env.sh               # Environment setup script
│
├── api/                        # API Route Handlers (3 modules, 526 lines)
│   ├── auth.py                # Authentication & session management
│   ├── game.py                # Game state and turn management
│   └── locations.py           # Location-based endpoints (shop, jobs, etc.)
│
├── models/                     # Game State Models (1 module, 526 lines)
│   ├── __init__.py
│   └── game_state.py          # GameState class with time/resource management
│
├── actions/                    # Game Action Handlers (9 modules, ~1,000 lines)
│   ├── __init__.py            # Action registry and orchestration
│   ├── base.py                # Base Action class with validation
│   ├── locations.py           # Location metadata and opening hours
│   ├── home.py                # Rest and recovery mechanics
│   ├── workplace.py           # Work to earn money
│   ├── shop.py                # Food purchasing (15 items)
│   ├── john_lewis.py          # Clothing/furniture purchases (12 items)
│   ├── university.py          # Education courses and enrollment (11 courses)
│   ├── job_office.py          # Employment applications (15+ jobs)
│   └── estate_agent.py        # Flat rentals (6 tiers)
│
├── chatbot/                    # LLM Integration (3 files, 429 lines)
│   ├── __init__.py
│   ├── llm_client.py          # OpenAI/Anthropic API clients with tool calling
│   ├── prompts.py             # NPC prompt loader
│   └── npc_prompts.yaml       # Character prompts for each location (6 NPCs)
│
├── mcp_server/                 # Model Context Protocol (2 files, 131 lines)
│   ├── __init__.py
│   └── tools.py               # MCP tool definitions and execution (6 tools)
│
├── config/                     # Configuration Management (4 files)
│   ├── __init__.py
│   ├── config.py              # Main config with AWS Secrets Manager (197 lines)
│   ├── secrets_config.json    # Local API keys (development) - NOT in git
│   ├── aws_secrets_config.json # AWS Secrets Manager config
│   └── llm_config.json        # LLM model parameters
│
├── utils/                      # Utility Modules (4 files, 457 lines)
│   ├── __init__.py
│   ├── s3_storage.py          # S3 storage with local fallback (248 lines)
│   ├── aws_secrets.py         # AWS Secrets Manager client (127 lines)
│   └── function_logger.py     # Function call logging with S3 upload (82 lines)
│
├── static/                     # Frontend Static Assets (3,219 lines)
│   ├── game.js                # Game UI logic (1,211 lines)
│   └── style.css              # Responsive styling with CSS Grid (2,008 lines)
│
├── templates/                  # HTML Templates (458 lines)
│   └── index.html             # Single-page app interface
│
├── data/                       # Persistent Data Storage (local mode)
│   ├── users.json             # User accounts (username → password hash)
│   ├── game_states.json       # Player game states (username → state dict)
│   └── detailed.log           # Application logs
│
└── deployment/                 # AWS Deployment Scripts
    ├── README.md              # Deployment documentation
    ├── deploy-initial.sh      # First-time infrastructure setup
    ├── deploy-update.sh       # Update existing deployment
    └── deploy-config.sh       # Build configuration
```

**Total**: ~6,900 lines of code
- Backend (Python): ~3,200 lines across 27 modules
- Frontend (JS/CSS/HTML): ~3,677 lines

---

## ⚙️ Configuration

### Environment Variables
- `S3_BUCKET_NAME`: S3 bucket for storage (default: `life-game-data-eunorth1`)
- `AWS_REGION`: AWS region (default: `eu-north-1`)
- `PYTHONUNBUFFERED=1`: Python output buffering

### Configuration Files
- **`config/config.py`**: Main application config with feature flags
  - `USE_AWS_LOG_STORAGE`: Enable S3 log uploads (default: False)
  - `USE_AWS_SECRETS`: Use AWS Secrets Manager vs local config (default: False)
  - `INITIAL_MONEY`: Starting money (default: £100)
  - `INITIAL_HAPPINESS`: Starting happiness (default: 50)

- **`config/secrets_config.json`**: Local development secrets (NOT committed)
  ```json
  {
    "OPENAI_API_KEY": "sk-...",
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "SECRET_KEY": "session-signing-key"
  }
  ```

- **`config/aws_secrets_config.json`**: AWS Secrets Manager references
  ```json
  {
    "OPENAI_API_KEY": "arn:aws:secretsmanager:...",
    "ANTHROPIC_API_KEY": "arn:aws:secretsmanager:...",
    "SECRET_KEY": "arn:aws:secretsmanager:..."
  }
  ```

- **`config/llm_config.json`**: LLM model parameters
  ```json
  {
    "temperature": 0.7,
    "max_tokens": 500
  }
  ```

- **`chatbot/npc_prompts.yaml`**: NPC character definitions (6 personalities)

---

## 🎮 Game Mechanics

### Time System
- **24-hour day cycle**: 1440 minutes per day
- **Day starts at 6:00 AM** and ends at 5:59 AM next day
- **Action costs**: 3 hours total (1h travel + 2h action)
- **Automatic turn increment**: When time remaining < 15 minutes

### Resource Updates
- **Per-turn changes**:
  - Hunger +25 (uncapped, can exceed 100)
  - Rent deducted from money
- **Working**: +25% of wage, tiredness +5
- **Resting**: Tiredness reduction scales with flat tier (4-15 points)
- **Eating**: Hunger reduction = calories / 10

### Progression Ladders

#### Education Path
1. **Middle School** (3 lectures) → None → £10-15 jobs
2. **High School** (5 lectures) → Middle School → £16-30 jobs
3. **Vocational/Bachelor** (6-8 lectures) → High School → £31-60 jobs
4. **Master** (8 lectures) → Bachelor → £61-100 jobs
5. **PhD** (10 lectures) → Master → £101-150 jobs

#### Appearance Levels (Look System)
- **Level 1 (Shabby)**: 0 clothing items → £0-25 jobs
- **Level 2 (Scruffy)**: 1-2 items → £26-50 jobs
- **Level 3 (Presentable)**: 3-4 items → £51-80 jobs
- **Level 4 (Smart)**: 5-7 items → £81-120 jobs
- **Level 5 (Very well groomed)**: 8+ items → £121-150 jobs

#### Housing Ladder
| Tier | Name | Rent | Tiredness Reduction | Happiness Bonus |
|------|------|------|---------------------|-----------------|
| 0 | Homeless | £0 | -4 | 0 |
| 1 | Dingy Bedsit | £10 | -6 | +2 |
| 2 | Basic Studio | £25 | -8 | +3 |
| 3 | Comfortable Flat | £50 | -10 | +4 |
| 4 | Stylish Apartment | £100 | -12 | +5 |
| 5 | Luxury Penthouse | £200 | -15 | +5 |

### Endgame Conditions
1. **Burnout**: Tiredness ≥ 81 AND Hunger ≥ 81 → Reset to initial state
2. **Bankruptcy**: Money < £0 → Reset to initial state
3. **Reset preserves**: Turn count (to track total game progress)

---

## 🤖 LLM Integration Architecture

### Tool Calling Flow
1. User sends message to NPC at current location
2. Backend loads NPC prompt + injects game state context
3. LLM receives user message + available tools for that location
4. LLM decides whether to call tools (e.g., `study`, `work`, `buy_item`)
5. Backend executes tools and updates game state
6. Backend sends tool results back to LLM
7. LLM generates final response to user
8. User sees response + updated game state

### Available MCP Tools
- `apply_for_job`: Apply for job by title
- `study`: Attend 1 lecture for enrolled course
- `work`: Work 2-hour shift to earn money
- `buy_item`: Purchase food item by name
- `rest`: Rest to recover tiredness
- `buy_john_lewis_item`: Purchase clothing/furniture by name

### Supported LLM Providers
- **OpenAI**: GPT-4o-mini (default, cost-effective)
- **Anthropic**: Claude-3.5-Sonnet (more sophisticated reasoning)

---

## 🐳 Docker Configuration

### Dockerfile Highlights
- **Base image**: `python:3.11-slim`
- **Port**: 5001
- **Volumes**:
  - `./data:/app/data` (persistent storage)
  - `${HOME}/.aws:/root/.aws:ro` (AWS credentials)
- **DNS**: Google DNS (8.8.8.8, 8.8.4.4) for reliable resolution

### docker-compose.yml
```yaml
services:
  life-game:
    build: .
    ports:
      - "5001:5001"
    volumes:
      - ./data:/app/data
      - ${HOME}/.aws:/root/.aws:ro
    environment:
      - S3_BUCKET_NAME=life-game-data-eunorth1
      - AWS_REGION=eu-north-1
```

---

## 🚢 AWS Deployment

### Infrastructure
- **Region**: `eu-north-1` (Stockholm)
- **S3 Bucket**: `life-game-data-eunorth1`
- **Secrets Manager**: API keys stored securely

### Deployment Scripts
- **`deployment/deploy-initial.sh`**: First-time setup (creates S3 bucket, uploads initial data)
- **`deployment/deploy-update.sh`**: Update existing deployment (builds Docker image, pushes to AWS)
- **`deployment/deploy-config.sh`**: Configure build target (local/aws)

### Deployment Steps
1. Configure AWS credentials (`aws configure`)
2. Run initial deployment: `./deployment/deploy-initial.sh`
3. Future updates: `./deployment/deploy-update.sh`

---

## 📊 Dependencies

See [requirements.txt](requirements.txt) for full list. Key dependencies:

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **openai** - OpenAI API client
- **anthropic** - Anthropic API client
- **boto3** - AWS SDK (S3, Secrets Manager)
- **loguru** - Structured logging
- **itsdangerous** - Session token signing
- **pyyaml** - YAML parsing (NPC prompts)
- **jinja2** - HTML templating

---

## 🧪 Development

### Running Tests
```bash
# No test suite currently implemented
# TODO: Add pytest tests for game mechanics
```

### Code Structure Best Practices
- **API routes**: Defined in `api/` modules, registered in `app.py`
- **Business logic**: Implemented in `actions/` and `models/`
- **Data access**: Abstracted through `utils/s3_storage.py`
- **Configuration**: Centralized in `config/config.py`

### Adding New Locations
1. Create action handler in `actions/new_location.py`
2. Define location metadata in `actions/locations.py`
3. Add API endpoints in `api/locations.py`
4. Update frontend in `static/game.js`
5. Add NPC prompt in `chatbot/npc_prompts.yaml`
6. Add MCP tool in `mcp_server/tools.py` (if needed)

---

## 📝 License

[Add your license information here]

---

## 🙏 Credits

- **LLM Integration**: OpenAI GPT-4o-mini, Anthropic Claude-3.5-Sonnet
- **Image Assets**: Unsplash (avatar and home images)
- **Hosting**: AWS (S3, Secrets Manager)
