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
        cost: 'Cost: $50 per level',
        npcName: 'Professor'
    },
    job_office: {
        title: 'Job Office',
        icon: '💼',
        description: 'Find a job matching your qualifications. Better education leads to higher-paying positions.',
        cost: 'Free',
        npcName: 'Clerk'
    },
    workplace: {
        title: 'Workplace',
        icon: '🏢',
        description: 'Go to work and earn money based on your current job position.',
        cost: 'Earns money based on your job',
        npcName: 'Boss'
    },
    shop: {
        title: 'Shop',
        icon: '🛒',
        description: 'Purchase items to improve your lifestyle and show off your success.',
        cost: 'Prices vary by item',
        npcName: 'Shopkeeper'
    }
};

// Show location modal with animation
function showLocationModal(action) {
    selectedAction = action;
    const details = locationDetails[action];

    const modal = document.getElementById('location-modal');
    const modalImage = document.getElementById('modal-image');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalCost = document.getElementById('modal-cost');
    const npcName = document.getElementById('npc-name');

    // Set content
    modalImage.className = 'modal-image ' + action;
    modalImage.textContent = details.icon;
    modalTitle.textContent = details.title;
    modalDescription.textContent = details.description;
    modalCost.textContent = details.cost;
    npcName.textContent = details.npcName;

    // Reset to action tab
    showTab('action');

    // Clear chat messages
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('chat-input').value = '';

    // Show modal with animation
    modal.style.display = 'flex';

    // Add entrance animation
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.animation = 'none';
    setTimeout(() => {
        modalContent.style.animation = 'slideUp 0.3s ease';
    }, 10);
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

// Tab switching
function showTab(tabName, event) {
    // Update tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // If no event, set first tab as active
        tabButtons[0].classList.add('active');
    }

    // Update tab content
    if (tabName === 'action') {
        document.getElementById('action-tab').style.display = 'block';
        document.getElementById('chat-tab').style.display = 'none';
    } else if (tabName === 'chat') {
        document.getElementById('action-tab').style.display = 'none';
        document.getElementById('chat-tab').style.display = 'block';
        document.getElementById('chat-input').focus();
    }
}

// Chat functionality
function addChatMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message ' + (isUser ? 'user-message' : 'npc-message');
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addChatMessage(message, true);
    chatInput.value = '';

    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-message npc-message typing';
    typingIndicator.textContent = '...';
    typingIndicator.id = 'typing-indicator';
    document.getElementById('chat-messages').appendChild(typingIndicator);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: selectedAction,
                message: message
            })
        });

        const data = await response.json();

        // Remove typing indicator
        document.getElementById('typing-indicator')?.remove();

        if (data.success) {
            addChatMessage(data.response, false);
        } else {
            addChatMessage('Error: ' + data.message, false);
        }
    } catch (error) {
        document.getElementById('typing-indicator')?.remove();
        addChatMessage('Error: Could not reach the server', false);
        console.error(error);
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
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
