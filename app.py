import sys
import os

# Add parent directory to path so we can import from life_game package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
from datetime import datetime
import hashlib
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from actions import perform_action
from config.config import config
from chat_service import get_llm_response
from models import GameState

app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Session serializer for secure cookie-based sessions
serializer = URLSafeTimedSerializer(config.SECRET_KEY)

DATA_DIR = config.DATA_DIR
USERS_FILE = os.path.join(DATA_DIR, config.USERS_FILE)
GAME_STATES_FILE = os.path.join(DATA_DIR, config.GAME_STATES_FILE)

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files if they don't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(GAME_STATES_FILE):
    with open(GAME_STATES_FILE, 'w') as f:
        json.dump({}, f)

# Pydantic models for request/response validation
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ActionRequest(BaseModel):
    action: str

class ChatRequest(BaseModel):
    action: str
    message: str

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_game_states():
    with open(GAME_STATES_FILE, 'r') as f:
        return json.load(f)

def save_game_states(states):
    with open(GAME_STATES_FILE, 'w') as f:
        json.dump(states, f, indent=2)

def create_new_game_state():
    """Create a new game state using the GameState class"""
    return GameState.create_new().to_dict()

def create_session_token(username: str) -> str:
    """Create a signed session token"""
    return serializer.dumps({'username': username})

def verify_session_token(token: str, max_age: int = 86400) -> Optional[str]:
    """Verify session token and return username if valid"""
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get('username')
    except (BadSignature, SignatureExpired):
        return None

async def get_current_user(request: Request) -> str:
    """Dependency to get current user from session cookie"""
    session_token = request.cookies.get('session')
    if not session_token:
        raise HTTPException(status_code=401, detail='Not logged in')

    username = verify_session_token(session_token)
    if not username:
        raise HTTPException(status_code=401, detail='Invalid or expired session')

    return username

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

@app.post('/api/register')
async def register(data: RegisterRequest):
    """Register a new user"""
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail='Username and password required')

    users = load_users()

    if data.username in users:
        raise HTTPException(status_code=400, detail='Username already exists')

    users[data.username] = {
        'password': hash_password(data.password),
        'created_at': datetime.now().isoformat()
    }
    save_users(users)

    # Create initial game state
    game_states = load_game_states()
    game_states[data.username] = create_new_game_state()
    save_game_states(game_states)

    return {'success': True, 'message': 'Registration successful'}

@app.post('/api/login')
async def login(data: LoginRequest):
    """Login user and create session"""
    users = load_users()

    if data.username not in users:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if users[data.username]['password'] != hash_password(data.password):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    # Create session token
    session_token = create_session_token(data.username)

    response = JSONResponse(content={'success': True, 'message': 'Login successful'})
    response.set_cookie(
        key='session',
        value=session_token,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite='lax'
    )

    return response

@app.post('/api/logout')
async def logout():
    """Logout user by clearing session cookie"""
    response = JSONResponse(content={'success': True})
    response.delete_cookie(key='session')
    return response

@app.get('/api/game_state')
async def get_game_state(username: str = Depends(get_current_user)):
    """Get current game state for logged in user"""
    game_states = load_game_states()

    if username not in game_states:
        game_states[username] = create_new_game_state()
        save_game_states(game_states)

    return {'success': True, 'state': game_states[username]}

@app.post('/api/action')
async def handle_action(data: ActionRequest, username: str = Depends(get_current_user)):
    """Handle game action"""
    game_states = load_game_states()
    state = game_states[username]

    # Perform the action using the actions module
    updated_state, message, success = perform_action(data.action, state)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Use GameState class to handle turn increment and per-turn updates
    game_state_obj = GameState(updated_state)
    game_state_obj.increment_turn()
    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    return {'success': True, 'state': updated_state, 'message': message}

@app.post('/api/chat')
async def handle_chat(data: ChatRequest, username: str = Depends(get_current_user)):
    """Handle chat messages with LLM and execute any triggered actions"""
    if not data.action or not data.message:
        raise HTTPException(status_code=400, detail='Missing action or message')

    # Get current game state for context
    game_states = load_game_states()
    state = game_states.get(username)

    # Get LLM response with potential tool calls
    result = get_llm_response(data.action, data.message, state)

    # If tools were called and state was updated, save the new state
    if result.get('updated_state'):
        # Use GameState class to handle turn increment and per-turn updates
        game_state_obj = GameState(result['updated_state'])
        game_state_obj.increment_turn()
        game_states[username] = game_state_obj.to_dict()
        save_game_states(game_states)

    return {
        'success': True,
        'response': result['response'],
        'tool_calls': result.get('tool_calls', []),
        'state': result.get('updated_state') or state
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, reload=config.DEBUG)
