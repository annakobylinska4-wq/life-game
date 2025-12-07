// Show/hide screens
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.style.display = 'none';
    });
    document.getElementById(screenId).style.display = 'block';
}

// Toggle between login and register forms
function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    clearMessage();
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    clearMessage();
}

// Display messages
function showMessage(message, isError = false) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = message;
    messageEl.className = 'message ' + (isError ? 'error' : 'success');
    messageEl.style.display = 'block';
}

function clearMessage() {
    const messageEl = document.getElementById('message');
    messageEl.style.display = 'none';
}

function showActionMessage(message, isError = false) {
    const messageEl = document.getElementById('action-message');
    messageEl.textContent = message;
    messageEl.className = 'action-message ' + (isError ? 'error' : 'success');
    messageEl.style.display = 'block';

    // Auto-hide after 3 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

// Register new user
async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    if (!username || !password) {
        showMessage('Please fill in all fields', true);
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Registration successful! Please login.');
            setTimeout(() => {
                showLogin();
                document.getElementById('login-username').value = username;
            }, 1500);
        } else {
            showMessage(data.message, true);
        }
    } catch (error) {
        showMessage('Error during registration', true);
        console.error(error);
    }
}

// Login user
async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
        showMessage('Please fill in all fields', true);
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            showScreen('game-screen');
            loadGameState();
        } else {
            showMessage(data.message, true);
        }
    } catch (error) {
        showMessage('Error during login', true);
        console.error(error);
    }
}

// Logout user
async function logout() {
    try {
        await fetch('/api/logout', {
            method: 'POST'
        });
        showScreen('auth-screen');
        showLogin();
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
    } catch (error) {
        console.error(error);
    }
}

// Load game state
async function loadGameState() {
    try {
        const response = await fetch('/api/game_state');
        const data = await response.json();

        if (data.success) {
            updateGameUI(data.state);
        } else {
            showActionMessage(data.message, true);
        }
    } catch (error) {
        showActionMessage('Error loading game state', true);
        console.error(error);
    }
}

// Update game UI with current state
function updateGameUI(state) {
    document.getElementById('turn').textContent = state.turn;
    document.getElementById('money').textContent = '$' + state.money;
    document.getElementById('job').textContent = state.current_job;
    document.getElementById('wage').textContent = '$' + state.job_wage + '/turn';
    document.getElementById('qualification').textContent = state.qualification;
    document.getElementById('items').textContent = state.items.length > 0
        ? state.items.join(', ')
        : 'None';
}

// Perform game action
async function performAction(action) {
    try {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action })
        });

        const data = await response.json();

        if (data.success) {
            updateGameUI(data.state);
            showActionMessage(data.message, false);
        } else {
            showActionMessage(data.message, true);
        }
    } catch (error) {
        showActionMessage('Error performing action', true);
        console.error(error);
    }
}

// Handle Enter key on login/register forms
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login-username').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') login();
    });
    document.getElementById('login-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') login();
    });
    document.getElementById('register-username').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') register();
    });
    document.getElementById('register-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') register();
    });
});
