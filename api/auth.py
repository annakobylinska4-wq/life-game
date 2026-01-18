"""
Authentication and session management endpoints
"""
from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import hashlib
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from config.config import config
from schemas import RegisterRequest, LoginRequest
from loguru import logger


# Session serializer for secure cookie-based sessions
serializer = URLSafeTimedSerializer(config.SECRET_KEY)


def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


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


def register_auth_routes(app, load_users, save_users, load_game_states, save_game_states, create_new_game_state):
    """Register authentication routes to FastAPI app"""

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
