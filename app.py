import sys
import os

# Add parent directory to path so we can import from life_game package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime
import hashlib
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from actions import perform_action, get_action_type_for_location, check_endgame_conditions
from actions.shop import get_shop_catalogue, purchase_item
from actions.john_lewis import get_john_lewis_catalogue, purchase_john_lewis_item
from actions.estate_agent import get_flat_catalogue, rent_flat
from actions.university import get_course_catalogue, get_available_courses, enroll_course, get_course_by_id
from actions.job_office import get_available_jobs, apply_for_job
from models.game_state import ACTION_TIME_COSTS, format_time, is_location_open, get_location_display_name
from config.config import config
from chatbot.llm_client import get_llm_response
from models import GameState
from schemas import (
    RegisterRequest, LoginRequest, ActionRequest, ChatRequest,
    PurchaseRequest, RentFlatRequest, EnrollCourseRequest, ApplyJobRequest
)
from utils.function_logger import initiliaze_logger, upload_logs_to_s3
from utils.s3_storage import init_storage, get_storage
from loguru import logger




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
    logger.info(f"Registering user: {data.username}")
    if not data.username or not data.password:
        logger.error("Registration failed: Missing username or password")
        raise HTTPException(status_code=400, detail='Username and password required')
    users = load_users()
    if data.username in users:
        logger.error(f"Registration failed: Username {data.username} already exists")
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
    logger.info(f"User {data.username} registered successfully")
    return {'success': True, 'message': 'Registration successful'}

@app.post('/api/login')
async def login(data: LoginRequest):
    """Login user and create session"""
    logger.info(f"User {data.username} attempting to log in")
    users = load_users()

    if data.username not in users:
        logger.error(f"Login failed: Username {data.username} does not exist")
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if users[data.username]['password'] != hash_password(data.password):
        logger.error(f"Login failed: Invalid password for user {data.username}")
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
    logger.info(f"User {data.username} logged in successfully")
    return response

@app.post('/api/logout')
async def logout(username: str = Depends(get_current_user)):
    """Logout user by clearing session cookie"""
    logger.info(f"User {username} logging out")
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

    action_type = get_action_type_for_location(location)
    travel_time, action_time, total_time = game_state_obj.get_total_time_cost
    has_time = game_state_obj.has_enough_time

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
    from actions import execute_action_with_validation

    game_states = load_game_states()
    state = game_states[username]

    location = data.action

    # Use generic action handler
    result = execute_action_with_validation(
        state=state,
        location=location,
        action_handler=lambda s: perform_action(data.action, s),
        check_opening_hours=True
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    # Save updated state
    game_states[username] = result['state']
    save_game_states(game_states)

    # Add time info to message for general actions
    message = result['message']
    if not result['burnout'] and not result['bankruptcy']:
        # Get action time from game state constants
        from models.game_state import ACTION_TIME_COSTS
        action_time = ACTION_TIME_COSTS
        action_str = f"{action_time // 60}h {action_time % 60}m" if action_time % 60 > 0 else f"{action_time // 60}h"
        time_info = f" (⏱ {action_str})"
        message = message + time_info

    return {
        'success': True,
        'state': result['state'],
        'message': message,
        'burnout': result['burnout'],
        'bankruptcy': result['bankruptcy'],
        'turn_summary': result['turn_summary']
    }

@app.get('/api/shop/catalogue')
async def get_catalogue(username: str = Depends(get_current_user)):
    """Get shop catalogue"""
    return {'success': True, 'items': get_shop_catalogue()}

@app.post('/api/shop/purchase')
async def handle_purchase(data: PurchaseRequest, username: str = Depends(get_current_user)):
    """Purchase a specific item from the shop"""
    from actions import execute_action_with_validation

    game_states = load_game_states()
    state = game_states[username]

    # Use generic action handler
    result = execute_action_with_validation(
        state=state,
        location='shop',
        action_handler=lambda s: purchase_item(s, data.item_name),
        check_opening_hours=False  # Shop is always open
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    # Save updated state
    game_states[username] = result['state']
    save_game_states(game_states)

    return {
        'success': True,
        'state': result['state'],
        'message': result['message'],
        'burnout': result['burnout'],
        'bankruptcy': result['bankruptcy'],
        'turn_summary': result['turn_summary']
    }

@app.get('/api/john_lewis/catalogue')
async def get_john_lewis_cat(username: str = Depends(get_current_user)):
    """Get John Lewis catalogue"""
    return {'success': True, 'items': get_john_lewis_catalogue()}

@app.post('/api/john_lewis/purchase')
async def handle_john_lewis_purchase(data: PurchaseRequest, username: str = Depends(get_current_user)):
    """Purchase a specific item from John Lewis"""
    from actions import execute_action_with_validation

    game_states = load_game_states()
    state = game_states[username]

    # Use generic action handler with update_look callback for clothing purchases
    result = execute_action_with_validation(
        state=state,
        location='john_lewis',
        action_handler=lambda s: purchase_john_lewis_item(s, data.item_name),
        check_opening_hours=False,  # John Lewis is always open
        post_action_callback=lambda game_state_obj: game_state_obj.update_look()
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    # Save updated state
    game_states[username] = result['state']
    save_game_states(game_states)

    return {
        'success': True,
        'state': result['state'],
        'message': result['message'],
        'burnout': result['burnout'],
        'bankruptcy': result['bankruptcy'],
        'turn_summary': result['turn_summary']
    }

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
    from actions import execute_action_with_validation

    game_states = load_game_states()
    state = game_states[username]

    # Use generic action handler
    result = execute_action_with_validation(
        state=state,
        location='estate_agent',
        action_handler=lambda s: rent_flat(s, data.tier),
        check_opening_hours=True
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    # Save updated state
    game_states[username] = result['state']
    save_game_states(game_states)

    return {
        'success': True,
        'state': result['state'],
        'message': result['message'],
        'burnout': result['burnout'],
        'bankruptcy': result['bankruptcy'],
        'turn_summary': result['turn_summary']
    }

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
    from actions import execute_action_with_validation

    game_states = load_game_states()
    state = game_states[username]

    # Use generic action handler - enrollment now consumes time like other actions
    result = execute_action_with_validation(
        state=state,
        location='university',
        action_handler=lambda s: enroll_course(s, data.course_id),
        check_opening_hours=True
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    # Save updated state
    game_states[username] = result['state']
    save_game_states(game_states)

    return {
        'success': True,
        'state': result['state'],
        'message': result['message'],
        'burnout': result['burnout'],
        'bankruptcy': result['bankruptcy'],
        'turn_summary': result['turn_summary']
    }

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
    """Pass enough time to start the next turn"""
    game_states = load_game_states()
    state = game_states[username]

    game_state_obj = GameState(state)

    # Calculate time needed to reach next turn (time_remaining < 15 triggers new turn)
    # Pass enough time to bring time_remaining to 14
    time_to_pass = game_state_obj.time_remaining - 14

    if time_to_pass <= 0:
        # Already at or below threshold, just need to trigger the turn
        time_to_pass = game_state_obj.time_remaining

    # Deduct time
    game_state_obj.time_remaining -= time_to_pass

    # Increment turn (will always happen since we passed enough time)
    turn_summary = game_state_obj.increment_turn()

    # Check for endgame conditions (burnout and bankruptcy)
    burnout, bankruptcy, message = check_endgame_conditions(game_state_obj)

    updated_state = game_state_obj.to_dict()

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    # Set message if no endgame condition occurred
    if not burnout and not bankruptcy:
        hours_passed = time_to_pass // 60
        minutes_passed = time_to_pass % 60
        if hours_passed > 0:
            message = f"You passed {hours_passed}h {minutes_passed}m and the day ended..."
        else:
            message = f"You passed {minutes_passed} minutes and the day ended..."

    return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'bankruptcy': bankruptcy, 'turn_summary': turn_summary}


@app.post('/api/job_office/apply')
async def handle_apply_job(data: ApplyJobRequest, username: str = Depends(get_current_user)):
    """Apply for a specific job"""
    from actions import execute_action_with_validation

    game_states = load_game_states()
    state = game_states[username]

    # Use generic action handler
    result = execute_action_with_validation(
        state=state,
        location='job_office',
        action_handler=lambda s: apply_for_job(s, data.job_title),
        check_opening_hours=True
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    # Save updated state
    game_states[username] = result['state']
    save_game_states(game_states)

    return {
        'success': True,
        'state': result['state'],
        'message': result['message'],
        'burnout': result['burnout'],
        'bankruptcy': result['bankruptcy'],
        'turn_summary': result['turn_summary']
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, reload=config.DEBUG)
