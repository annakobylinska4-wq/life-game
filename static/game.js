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

// Store selected action for confirmation
let selectedAction = null;

// Location details
const locationDetails = {
    university: {
        title: 'University',
        icon: '🎓',
        description: 'Study hard to improve your qualifications. Each level unlocks better job opportunities.',
        cost: 'Cost: $50 per level'
    },
    job_office: {
        title: 'Job Office',
        icon: '💼',
        description: 'Find a job matching your qualifications. Better education leads to higher-paying positions.',
        cost: 'Free'
    },
    workplace: {
        title: 'Workplace',
        icon: '🏢',
        description: 'Go to work and earn money based on your current job position.',
        cost: 'Earns money based on your job'
    },
    shop: {
        title: 'Shop',
        icon: '🛒',
        description: 'Purchase items to improve your lifestyle and show off your success.',
        cost: 'Prices vary by item'
    }
};

// Show location modal
function showLocationModal(action) {
    selectedAction = action;
    const details = locationDetails[action];

    const modal = document.getElementById('location-modal');
    const modalImage = document.getElementById('modal-image');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalCost = document.getElementById('modal-cost');

    // Set content
    modalImage.className = 'modal-image ' + action;
    modalImage.textContent = details.icon;
    modalTitle.textContent = details.title;
    modalDescription.textContent = details.description;
    modalCost.textContent = details.cost;

    // Show modal
    modal.style.display = 'flex';
}

// Close location modal
function closeLocationModal() {
    document.getElementById('location-modal').style.display = 'none';
    selectedAction = null;
}

// Confirm action
async function confirmAction() {
    if (!selectedAction) return;

    const action = selectedAction;
    closeLocationModal();

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

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('location-modal');
    if (event.target === modal) {
        closeLocationModal();
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
