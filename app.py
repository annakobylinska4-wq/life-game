from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
GAME_STATES_FILE = os.path.join(DATA_DIR, 'game_states.json')

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
        'money': 100,
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
def perform_action():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    username = session['username']
    data = request.json
    action = data.get('action')

    game_states = load_game_states()
    state = game_states[username]

    message = ""

    if action == 'university':
        cost = 50
        if state['money'] >= cost:
            state['money'] -= cost
            qualifications = ['None', 'High School', 'Bachelor', 'Master', 'PhD']
            current_idx = qualifications.index(state['qualification'])
            if current_idx < len(qualifications) - 1:
                state['qualification'] = qualifications[current_idx + 1]
                message = "You studied hard and earned a {} degree! (-${})".format(state['qualification'], cost)
            else:
                message = "You are already at the highest qualification level!"
                state['money'] += cost
        else:
            return jsonify({'success': False, 'message': 'Not enough money! Need ${}'.format(cost)}), 400

    elif action == 'job_office':
        # Better qualifications = better jobs
        jobs = {
            'None': ('Janitor', 20),
            'High School': ('Cashier', 35),
            'Bachelor': ('Office Worker', 60),
            'Master': ('Manager', 100),
            'PhD': ('Executive', 150)
        }
        job_title, wage = jobs.get(state['qualification'], ('Unemployed', 0))
        state['current_job'] = job_title
        state['job_wage'] = wage
        message = "You secured a job as {} earning ${} per turn!".format(job_title, wage)

    elif action == 'workplace':
        if state['current_job'] == 'Unemployed':
            return jsonify({'success': False, 'message': 'You need to get a job first!'}), 400
        earnings = state['job_wage']
        state['money'] += earnings
        message = "You worked as {} and earned ${}!".format(state['current_job'], earnings)

    elif action == 'shop':
        items_available = [
            ('Food', 10),
            ('Clothes', 25),
            ('Phone', 100),
            ('Laptop', 300),
            ('Car', 1000)
        ]

        # Buy a random affordable item
        affordable = [item for item in items_available if item[1] <= state['money']]
        if affordable:
            import random
            item_name, item_cost = random.choice(affordable)
            state['money'] -= item_cost
            state['items'].append(item_name)
            message = "You bought {} for ${}!".format(item_name, item_cost)
        else:
            return jsonify({'success': False, 'message': 'Not enough money to buy anything!'}), 400

    else:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400

    # Increment turn
    state['turn'] += 1

    game_states[username] = state
    save_game_states(game_states)

    return jsonify({'success': True, 'state': state, 'message': message})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
