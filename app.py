from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import hashlib
from actions import perform_action
from config import config
from chat_service import get_llm_response

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

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
    return {
        'money': config.INITIAL_MONEY,
        'items': [],
        'qualification': 'None',
        'current_job': 'Unemployed',
        'job_wage': 0,
        'turn': 1
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    users = load_users()

    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    save_users(users)

    # Create initial game state
    game_states = load_game_states()
    game_states[username] = create_new_game_state()
    save_game_states(game_states)

    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    users = load_users()

    if username not in users:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    if users[username]['password'] != hash_password(password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    session['username'] = username
    return jsonify({'success': True, 'message': 'Login successful'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    username = session['username']
    game_states = load_game_states()

    if username not in game_states:
        game_states[username] = create_new_game_state()
        save_game_states(game_states)

    return jsonify({'success': True, 'state': game_states[username]})

@app.route('/api/action', methods=['POST'])
def handle_action():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    username = session['username']
    data = request.json
    action = data.get('action')

    game_states = load_game_states()
    state = game_states[username]

    # Perform the action using the actions module
    updated_state, message, success = perform_action(action, state)

    if not success:
        return jsonify({'success': False, 'message': message}), 400

    # Increment turn
    updated_state['turn'] += 1

    # Save updated state
    game_states[username] = updated_state
    save_game_states(game_states)

    return jsonify({'success': True, 'state': updated_state, 'message': message})

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    username = session['username']
    data = request.json
    action = data.get('action')
    message = data.get('message')

    if not action or not message:
        return jsonify({'success': False, 'message': 'Missing action or message'}), 400

    # Get current game state for context
    game_states = load_game_states()
    state = game_states.get(username)

    # Get LLM response
    response = get_llm_response(action, message, state)

    return jsonify({'success': True, 'response': response})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)
