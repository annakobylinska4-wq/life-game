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

// Toggle status popup panel
function toggleStatusPanel() {
    const popup = document.getElementById('status-popup');
    if (popup.style.display === 'none' || popup.style.display === '') {
        popup.style.display = 'flex';
    } else {
        popup.style.display = 'none';
    }
}

// Close status panel when clicking outside
window.addEventListener('click', function(event) {
    const popup = document.getElementById('status-popup');
    if (event.target === popup) {
        popup.style.display = 'none';
    }
});

// Update game UI with current state
function updateGameUI(state) {
    // Wellbeing stats (default to initial values if not present)
    const happiness = state.happiness !== undefined ? state.happiness : 50;
    const tiredness = state.tiredness !== undefined ? state.tiredness : 0;
    const hunger = state.hunger !== undefined ? state.hunger : 0;

    // Update top stats bar
    document.getElementById('top-turn').textContent = state.turn;
    document.getElementById('top-money').textContent = '$' + state.money;
    document.getElementById('top-job').textContent = state.current_job;
    document.getElementById('top-qualification').textContent = state.qualification;

    // Update top bar progress bars
    document.getElementById('top-happiness-value').textContent = happiness;
    document.getElementById('top-happiness-bar').style.width = happiness + '%';

    document.getElementById('top-tiredness-value').textContent = tiredness;
    document.getElementById('top-tiredness-bar').style.width = tiredness + '%';

    document.getElementById('top-hunger-value').textContent = hunger;
    document.getElementById('top-hunger-bar').style.width = hunger + '%';

    // Update popup panel (wage and inventory only)
    document.getElementById('wage').textContent = '$' + state.job_wage + '/turn';
    document.getElementById('items').textContent = state.items.length > 0
        ? state.items.join(', ')
        : 'None';
}

// Store selected action for confirmation
let selectedAction = null;

// Location details
// Note: confirmButtonLabel values correspond to BUTTON_LABEL constants in actions/*.py
const locationDetails = {
    university: {
        title: "King's College London",
        icon: '🎓',
        description: 'Study at one of London\'s most prestigious universities. Improve your qualifications to unlock better career opportunities in the city.',
        cost: 'Cost: £50 per level',
        npcName: 'Professor',
        confirmButtonLabel: 'Attend lecture'
    },
    job_office: {
        title: 'Canary Wharf Recruitment',
        icon: '💼',
        description: 'Find your perfect role in London\'s financial district. Better qualifications lead to higher-paying positions in the City.',
        cost: 'Free',
        npcName: 'Recruiter',
        confirmButtonLabel: 'Get a new job'
    },
    workplace: {
        title: 'The City Office',
        icon: '🏢',
        description: 'Work in the heart of London\'s business district. Earn your salary based on your current position.',
        cost: 'Earns money based on your job',
        npcName: 'Manager',
        confirmButtonLabel: 'Work'
    },
    shop: {
        title: 'Borough Food Market',
        icon: '🛒',
        description: 'Visit London\'s famous food market. Purchase fresh food to keep your hunger at bay.',
        cost: 'Prices vary by item',
        npcName: 'Vendor',
        confirmButtonLabel: 'Buy some food'
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
    const confirmBtn = document.querySelector('.confirm-btn');

    // Set content
    modalImage.className = 'modal-image ' + action;
    modalImage.textContent = ''; // No text content for background images
    modalTitle.textContent = details.title;
    modalDescription.textContent = details.description;
    modalCost.textContent = details.cost;
    npcName.textContent = details.npcName;
    confirmBtn.textContent = details.confirmButtonLabel;

    // Show "Browse the aisles" button only for shop
    const browseBtn = document.getElementById('browse-btn');
    if (action === 'shop') {
        browseBtn.style.display = 'inline-block';
    } else {
        browseBtn.style.display = 'none';
    }

    // Hide shop catalogue by default
    document.getElementById('shop-catalogue').style.display = 'none';

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

    // Reset modal buttons visibility
    document.querySelector('.modal-buttons').style.display = 'flex';
    document.getElementById('shop-catalogue').style.display = 'none';
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
            // Update UI if state changed
            if (data.state) {
                updateGameUI(data.state);
            }
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

// Browse shop aisles
async function browseShopAisles() {
    try {
        const response = await fetch('/api/shop/catalogue');
        const data = await response.json();

        if (data.success) {
            displayShopCatalogue(data.items);
        } else {
            showActionMessage('Error loading shop catalogue', true);
        }
    } catch (error) {
        showActionMessage('Error loading shop catalogue', true);
        console.error(error);
    }
}

// Display shop catalogue
function displayShopCatalogue(items) {
    const catalogueContainer = document.getElementById('catalogue-items');
    catalogueContainer.innerHTML = '';

    items.forEach(item => {
        const itemCard = document.createElement('div');
        itemCard.className = 'catalogue-item';
        itemCard.innerHTML = `
            <div class="item-emoji">${item.emoji}</div>
            <div class="item-details">
                <div class="item-name">${item.name}</div>
                <div class="item-info">
                    <span class="item-cost">$${item.cost}</span>
                    <span class="item-calories">${item.calories} cal</span>
                </div>
            </div>
        `;
        itemCard.onclick = () => purchaseShopItem(item.name);
        catalogueContainer.appendChild(itemCard);
    });

    // Hide default buttons and show catalogue
    document.querySelector('.modal-buttons').style.display = 'none';
    document.getElementById('shop-catalogue').style.display = 'block';
}

// Hide shop catalogue and show default buttons
function hideShopCatalogue() {
    document.getElementById('shop-catalogue').style.display = 'none';
    document.querySelector('.modal-buttons').style.display = 'flex';
}

// Purchase a specific shop item
async function purchaseShopItem(itemName) {
    try {
        const response = await fetch('/api/shop/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_name: itemName })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            updateGameUI(data.state);
            showActionMessage(data.message, false);
            closeLocationModal();
        } else {
            // Handle error response
            const errorMsg = data.detail || data.message || 'Purchase failed';
            showActionMessage(errorMsg, true);
        }
    } catch (error) {
        showActionMessage('Error purchasing item', true);
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
