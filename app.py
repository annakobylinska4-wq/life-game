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
from actions.shop import get_shop_catalogue, purchase_item
from actions.john_lewis import get_john_lewis_catalogue, purchase_john_lewis_item
from actions.estate_agent import get_flat_catalogue, rent_flat
from actions.university import get_course_catalogue, get_available_courses, enroll_course, get_course_by_id
from actions.job_office import get_available_jobs, apply_for_job
from models.game_state import ACTION_TIME_COSTS, LOCATION_COORDS, format_time
from config.config import config
from chat_service import get_llm_response
from models import GameState
from utils.function_logger import set_current_user
from utils.s3_storage import init_storage, get_storage

app = FastAPI()

# Initialize S3 storage (uses env var S3_BUCKET_NAME if set, otherwise local storage)
storage = init_storage()

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Session serializer for secure cookie-based sessions
serializer = URLSafeTimedSerializer(config.SECRET_KEY)

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

class PurchaseRequest(BaseModel):
    item_name: str

class RentFlatRequest(BaseModel):
    tier: int

class EnrollCourseRequest(BaseModel):
    course_id: str

class ApplyJobRequest(BaseModel):
    job_title: str

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

    # Set user context for function logging
    set_current_user(username)

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
async def logout(username: str = Depends(get_current_user)):
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

    # Ensure look is calculated (for existing players without look attribute)
    game_state_obj = GameState(game_states[username])
    game_state_obj.update_look()
    state_with_look = game_state_obj.to_dict()

    return {'success': True, 'state': state_with_look}


@app.get('/api/time_info/{location}')
async def get_time_info(location: str, username: str = Depends(get_current_user)):
    """Get time cost info for visiting a location"""
    game_states = load_game_states()
    state = game_states[username]
    game_state_obj = GameState(state)

    # Map location to action type
    action_type_map = {
        'home': 'rest',
        'workplace': 'work',
        'university': 'university',
        'shop': 'shop_purchase',
        'john_lewis': 'john_lewis',
        'job_office': 'job_office',
        'estate_agent': 'estate_agent'
    }

    action_type = action_type_map.get(location, 'shop_purchase')
    travel_time, action_time, total_time = game_state_obj.get_total_time_cost(location, action_type)
    has_time = game_state_obj.has_enough_time(location, action_type)

    return {
        'success': True,
        'location': location,
        'travel_time': travel_time,
        'action_time': action_time,
        'total_time': total_time,
        'has_enough_time': has_time,
        'time_remaining': game_state_obj.time_remaining,
        'current_time': format_time(game_state_obj.time_remaining),
        'arrival_time': format_time(game_state_obj.time_remaining - travel_time) if travel_time <= game_state_obj.time_remaining else None,
        'finish_time': format_time(game_state_obj.time_remaining - total_time) if total_time <= game_state_obj.time_remaining else None
    }

@app.post('/api/action')
async def handle_action(data: ActionRequest, username: str = Depends(get_current_user)):
    """Handle game action"""
    game_states = load_game_states()
    state = game_states[username]

    # Map action to location and action type
    action_location_map = {
        'home': ('home', 'rest'),
        'workplace': ('workplace', 'work'),
        'university': ('university', 'university'),
        'shop': ('shop', 'shop_purchase'),
        'john_lewis': ('john_lewis', 'john_lewis'),
        'job_office': ('job_office', 'job_office'),
        'estate_agent': ('estate_agent', 'estate_agent')
    }

    location, action_type = action_location_map.get(data.action, (data.action, data.action))

    # Check if player has enough time
    game_state_obj = GameState(state)
    if not game_state_obj.has_enough_time(location, action_type):
        travel_time, action_time, total_time = game_state_obj.get_total_time_cost(location, action_type)
        hours = total_time // 60
        mins = total_time % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        raise HTTPException(status_code=400, detail=f"Not enough time today! This would take {time_str} but you only have {game_state_obj.time_remaining // 60}h {game_state_obj.time_remaining % 60}m left.")

    # Spend time for travel and action
    travel_time, action_time, time_success, turn_summary = game_state_obj.spend_time(location, action_type)
    state = game_state_obj.to_dict()

    # Perform the action using the actions module
    updated_state, message, success = perform_action(data.action, state)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Use GameState class to handle state (don't increment turn - spend_time handles day rollover)
    game_state_obj = GameState(updated_state)

    # Check for burnout (exhausted AND starving)
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()
        message = "BURNOUT"  # Special message to trigger frontend popup

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    # Add time info to message
    if not burnout:
        travel_str = f"{travel_time}min travel" if travel_time > 0 else ""
        action_str = f"{action_time // 60}h {action_time % 60}m" if action_time % 60 > 0 else f"{action_time // 60}h"
        time_info = f" (⏱ {travel_str}{' + ' if travel_str else ''}{action_str})"
        message = message + time_info

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'turn_summary': turn_summary}

@app.get('/api/shop/catalogue')
async def get_catalogue(username: str = Depends(get_current_user)):
    """Get shop catalogue"""
    return {'success': True, 'items': get_shop_catalogue()}

@app.post('/api/shop/purchase')
async def handle_purchase(data: PurchaseRequest, username: str = Depends(get_current_user)):
    """Purchase a specific item from the shop"""
    game_states = load_game_states()
    state = game_states[username]

    # Check if player has enough time
    game_state_obj = GameState(state)
    if not game_state_obj.has_enough_time('shop', 'shop_purchase'):
        travel_time, action_time, total_time = game_state_obj.get_total_time_cost('shop', 'shop_purchase')
        hours = total_time // 60
        mins = total_time % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        raise HTTPException(status_code=400, detail=f"Not enough time today! This would take {time_str}.")

    # Spend time for travel and action
    travel_time, action_time, _, turn_summary = game_state_obj.spend_time('shop', 'shop_purchase')
    state = game_state_obj.to_dict()

    # Purchase the item
    updated_state, message, success = purchase_item(state, data.item_name)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Use GameState class to handle state
    game_state_obj = GameState(updated_state)

    # Check for burnout (exhausted AND starving)
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()
        message = "BURNOUT"

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'turn_summary': turn_summary}

@app.get('/api/john_lewis/catalogue')
async def get_john_lewis_cat(username: str = Depends(get_current_user)):
    """Get John Lewis catalogue"""
    return {'success': True, 'items': get_john_lewis_catalogue()}

@app.post('/api/john_lewis/purchase')
async def handle_john_lewis_purchase(data: PurchaseRequest, username: str = Depends(get_current_user)):
    """Purchase a specific item from John Lewis"""
    game_states = load_game_states()
    state = game_states[username]

    # Check if player has enough time
    game_state_obj = GameState(state)
    if not game_state_obj.has_enough_time('john_lewis', 'john_lewis'):
        travel_time, action_time, total_time = game_state_obj.get_total_time_cost('john_lewis', 'john_lewis')
        hours = total_time // 60
        mins = total_time % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        raise HTTPException(status_code=400, detail=f"Not enough time today! This would take {time_str}.")

    # Spend time for travel and action
    travel_time, action_time, _, turn_summary = game_state_obj.spend_time('john_lewis', 'john_lewis')
    state = game_state_obj.to_dict()

    # Purchase the item
    updated_state, message, success = purchase_john_lewis_item(state, data.item_name)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Use GameState class to handle state
    game_state_obj = GameState(updated_state)
    game_state_obj.update_look()  # Update look based on clothing items

    # Check for burnout (exhausted AND starving)
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()
        message = "BURNOUT"

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'turn_summary': turn_summary}

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

@app.get('/api/estate_agent/catalogue')
async def get_flats_catalogue(username: str = Depends(get_current_user)):
    """Get available flats for rent"""
    return {'success': True, 'flats': get_flat_catalogue()}

@app.post('/api/estate_agent/rent')
async def handle_rent_flat(data: RentFlatRequest, username: str = Depends(get_current_user)):
    """Rent a flat of the specified tier"""
    game_states = load_game_states()
    state = game_states[username]

    # Check if player has enough time
    game_state_obj = GameState(state)
    if not game_state_obj.has_enough_time('estate_agent', 'estate_agent'):
        travel_time, action_time, total_time = game_state_obj.get_total_time_cost('estate_agent', 'estate_agent')
        hours = total_time // 60
        mins = total_time % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        raise HTTPException(status_code=400, detail=f"Not enough time today! This would take {time_str}.")

    # Spend time for travel and action
    travel_time, action_time, _, turn_summary = game_state_obj.spend_time('estate_agent', 'estate_agent')
    state = game_state_obj.to_dict()

    # Rent the flat
    updated_state, message, success = rent_flat(state, data.tier)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Use GameState class to handle state
    game_state_obj = GameState(updated_state)

    # Check for burnout (exhausted AND starving)
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()
        message = "BURNOUT"

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'turn_summary': turn_summary}

@app.get('/api/university/catalogue')
async def get_courses_catalogue(username: str = Depends(get_current_user)):
    """Get available courses based on player's education"""
    game_states = load_game_states()
    state = game_states[username]

    completed_courses = state.get('completed_courses', [])
    enrolled_course = state.get('enrolled_course', None)
    lectures_completed = state.get('lectures_completed', 0)

    # Get courses with eligibility info
    courses = get_available_courses(completed_courses)

    # Add current enrollment info
    enrolled_info = None
    if enrolled_course:
        course = get_course_by_id(enrolled_course)
        if course:
            enrolled_info = {
                'id': course['id'],
                'name': course['name'],
                'lectures_completed': lectures_completed,
                'lectures_required': course['lectures_required'],
                'cost_per_lecture': course['cost_per_lecture']
            }

    return {
        'success': True,
        'courses': courses,
        'completed_courses': completed_courses,
        'enrolled_course': enrolled_info
    }

@app.post('/api/university/enroll')
async def handle_enroll_course(data: EnrollCourseRequest, username: str = Depends(get_current_user)):
    """Enroll in a course"""
    game_states = load_game_states()
    state = game_states[username]

    # Enroll in the course (no turn increment for enrollment)
    updated_state, message, success = enroll_course(state, data.course_id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Save updated state (no turn increment for enrollment)
    game_state_obj = GameState(updated_state)
    game_states[username] = game_state_obj.to_dict()
    save_game_states(game_states)

    return {'success': True, 'state': game_state_obj.to_dict(), 'message': message}

@app.get('/api/job_office/jobs')
async def get_jobs_list(username: str = Depends(get_current_user)):
    """Get available jobs based on player's education and appearance"""
    game_states = load_game_states()
    state = game_states[username]

    completed_courses = state.get('completed_courses', [])
    current_look = state.get('look', 1)
    jobs = get_available_jobs(completed_courses, current_look)

    return {
        'success': True,
        'jobs': jobs,
        'current_job': state.get('current_job', 'Unemployed'),
        'current_wage': state.get('job_wage', 0)
    }

@app.post('/api/pass_time')
async def handle_pass_time(username: str = Depends(get_current_user)):
    """Pass 30 minutes of time doing nothing (or remaining time if less)"""
    game_states = load_game_states()
    state = game_states[username]

    game_state_obj = GameState(state)

    # Pass 30 minutes or whatever time remains
    time_to_pass = min(30, game_state_obj.time_remaining)

    if time_to_pass <= 0:
        raise HTTPException(status_code=400, detail="No time left today!")

    # Deduct time
    game_state_obj.time_remaining -= time_to_pass

    # Check if day is over (less than 15 minutes remaining)
    turn_summary = None
    if game_state_obj.time_remaining < 15:
        turn_summary = game_state_obj.increment_turn()

    # Check for burnout
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    message = f"You passed {time_to_pass} minutes watching the world go by..."

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'turn_summary': turn_summary}


@app.post('/api/job_office/apply')
async def handle_apply_job(data: ApplyJobRequest, username: str = Depends(get_current_user)):
    """Apply for a specific job"""
    game_states = load_game_states()
    state = game_states[username]

    # Check if player has enough time
    game_state_obj = GameState(state)
    if not game_state_obj.has_enough_time('job_office', 'job_office'):
        travel_time, action_time, total_time = game_state_obj.get_total_time_cost('job_office', 'job_office')
        hours = total_time // 60
        mins = total_time % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        raise HTTPException(status_code=400, detail=f"Not enough time today! This would take {time_str}.")

    # Spend time for travel and action
    travel_time, action_time, _, turn_summary = game_state_obj.spend_time('job_office', 'job_office')
    state = game_state_obj.to_dict()

    # Apply for the job
    updated_state, message, success = apply_for_job(state, data.job_title)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Use GameState class to handle state
    game_state_obj = GameState(updated_state)

    # Check for burnout (exhausted AND starving)
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()
        message = "BURNOUT"

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'turn_summary': turn_summary}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, reload=config.DEBUG)
