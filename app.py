import sys
import os

# Add parent directory to path so we can import from life_game package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
from contextlib import asynccontextmanager
from config.config import config
from models import GameState
from utils.function_logger import initiliaze_logger, upload_logs_to_s3
from utils.s3_storage import init_storage
from loguru import logger

# Import API route registration functions
from api.auth import register_auth_routes, get_current_user
from api.game import register_game_routes
from api.locations import register_location_routes


# Background task for periodic log uploads
_upload_task = None
_shutdown = False

async def periodic_log_upload():
    """Background task to upload logs to S3 every 60 seconds"""
    global _shutdown
    while not _shutdown:
        await asyncio.sleep(60)  # Upload every 60 seconds
        if not _shutdown:
            try:
                upload_logs_to_s3()
            except Exception as e:
                logger.error(f"Error in periodic log upload: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global _upload_task, _shutdown

    # Startup
    initiliaze_logger()
    logger.info("app_startup")

    # Start background log upload task if S3 is enabled
    if config.USE_AWS_LOG_STORAGE:
        _shutdown = False
        _upload_task = asyncio.create_task(periodic_log_upload())
        logger.info("Started periodic log upload task")

    yield

    # Shutdown
    logger.info("app_shutdown")
    _shutdown = True

    # Cancel background task
    if _upload_task:
        _upload_task.cancel()
        try:
            await _upload_task
        except asyncio.CancelledError:
            pass

    # Final log upload before shutdown
    if config.USE_AWS_LOG_STORAGE:
        logger.info("Uploading final logs to S3...")
        upload_logs_to_s3()
        logger.info("Final log upload complete")

app = FastAPI(lifespan=lifespan)

# Initialize S3 storage with default bucket name
storage = init_storage(bucket_name=config.S3_LOG_BUCKET)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Data file paths
DATA_DIR = config.DATA_DIR
USERS_FILE = os.path.join(DATA_DIR, config.USERS_FILE)
GAME_STATES_FILE = os.path.join(DATA_DIR, config.GAME_STATES_FILE)

# Ensure data directory exists (for local fallback)
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize local data files if not using S3 and they don't exist
if not storage.is_using_s3():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

    if not os.path.exists(GAME_STATES_FILE):
        with open(GAME_STATES_FILE, 'w') as f:
            json.dump({}, f)

def load_users():
    """Load users from S3 or local storage"""
    return storage.read_json(config.USERS_FILE, USERS_FILE)

def save_users(users):
    """Save users to S3 or local storage"""
    storage.write_json(config.USERS_FILE, users, USERS_FILE)

def load_game_states():
    """Load game states from S3 or local storage"""
    return storage.read_json(config.GAME_STATES_FILE, GAME_STATES_FILE)

def save_game_states(states):
    """Save game states to S3 or local storage"""
    storage.write_json(config.GAME_STATES_FILE, states, GAME_STATES_FILE)

def create_new_game_state():
    """Create a new game state using the GameState class"""
    return GameState.create_new().to_dict()

# Setup templates (if you have HTML templates)
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
try:
    templates = Jinja2Templates(directory=templates_dir)
except:
    templates = None

@app.get('/')
async def index(request: Request):
    """Serve the main page"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return {"message": "Life Game API"}

# Register all API routes from the modules
register_auth_routes(app, load_users, save_users, load_game_states, save_game_states, create_new_game_state)
register_game_routes(app, get_current_user, load_game_states, save_game_states, create_new_game_state)
register_location_routes(app, get_current_user, load_game_states, save_game_states)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, reload=config.DEBUG)
