// Look avatar URLs for each level (1-5)
// Middle-aged man going from very dishevelled/scruffy to well-groomed businessman
const LOOK_AVATARS = {
    1: 'https://images.unsplash.com/photo-1518806118471-f28b20a1d79d?w=300&h=300&fit=crop&crop=face', // Shabby - dishevelled, almost homeless man
    2: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop&crop=face', // Scruffy - unshaven, messy
    3: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face', // Presentable - normal casual
    4: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face', // Smart - professional look
    5: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop&crop=face'  // Very well groomed - business suit
};

// Home images based on flat tier (0-5)
// Different home appearances based on what flat the player is renting
const HOME_IMAGES = {
    0: 'https://images.unsplash.com/photo-1588880331179-bc9b93a8cb5e?w=800&h=600&fit=crop', // Homeless - abandoned ruined building interior
    1: 'https://images.unsplash.com/photo-1597047084993-bf36ace2a68d?w=800&h=600&fit=crop', // Dingy bedsit - decrepit dirty room
    2: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=600&fit=crop', // Basic studio - simple but clean
    3: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop', // Comfortable flat - nice living room
    4: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=600&fit=crop', // Stylish apartment - modern interior
    5: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=600&fit=crop'  // Luxury penthouse - stunning views
};

// Store current flat tier for home display
let currentFlatTier = 0;

function getLookAvatarUrl(lookLevel) {
    return LOOK_AVATARS[lookLevel] || LOOK_AVATARS[1];
}

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
    const popup = document.getElementById('action-result-popup');
    const content = popup.querySelector('.action-result-content');
    const icon = document.getElementById('action-result-icon');
    const messageEl = document.getElementById('action-result-message');

    // Set content based on success/error
    if (isError) {
        content.className = 'action-result-content error';
        icon.className = 'action-result-icon error';
        icon.textContent = '✗';
    } else {
        content.className = 'action-result-content success';
        icon.className = 'action-result-icon success';
        icon.textContent = '✓';
    }

    messageEl.textContent = message;
    popup.style.display = 'flex';
}

function closeActionResultPopup() {
    document.getElementById('action-result-popup').style.display = 'none';
}

// Eating animation popup
let eatingPopupCallback = null;

function showEatingPopup(callback) {
    const popup = document.getElementById('eating-popup');
    const okBtn = popup.querySelector('.eating-ok-btn');

    // Store callback to execute after user acknowledges
    eatingPopupCallback = callback;

    // Reset button animation by removing and re-adding it
    okBtn.style.animation = 'none';
    popup.style.display = 'flex';

    // Trigger reflow and restart animation
    setTimeout(() => {
        okBtn.style.animation = 'fadeIn 0.3s ease 2s forwards';
    }, 10);
}

function closeEatingPopup() {
    const popup = document.getElementById('eating-popup');
    popup.style.display = 'none';

    // Execute the callback to continue the turn
    if (eatingPopupCallback) {
        eatingPopupCallback();
        eatingPopupCallback = null;
    }
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

    // Update look avatar and label in status panel
    const lookLevel = state.look || 1;
    const lookLabel = state.look_label || 'Shabby';
    const lookAvatarEl = document.getElementById('look-avatar');
    const lookLabelEl = document.getElementById('look-label');
    if (lookAvatarEl) {
        lookAvatarEl.src = getLookAvatarUrl(lookLevel);
    }
    if (lookLabelEl) {
        lookLabelEl.textContent = lookLabel;
    }

    // Get labels for display
    const happinessLabel = state.happiness_label || 'Content';
    const tirednessLabel = state.tiredness_label || 'Well rested';
    const hungerLabel = state.hunger_label || 'Full';

    // Update top bar progress bars with labels (not numbers)
    document.getElementById('top-happiness-value').textContent = happinessLabel;
    document.getElementById('top-happiness-bar').style.width = happiness + '%';

    document.getElementById('top-tiredness-value').textContent = tirednessLabel;
    document.getElementById('top-tiredness-bar').style.width = tiredness + '%';

    document.getElementById('top-hunger-value').textContent = hungerLabel;
    document.getElementById('top-hunger-bar').style.width = hunger + '%';

    document.getElementById('panel-happiness-value').textContent = happiness;
    document.getElementById('panel-happiness-label').textContent = happinessLabel;

    document.getElementById('panel-tiredness-value').textContent = tiredness;
    document.getElementById('panel-tiredness-label').textContent = tirednessLabel;

    document.getElementById('panel-hunger-value').textContent = hunger;
    document.getElementById('panel-hunger-label').textContent = hungerLabel;

    // Update popup panel (wage, rent, housing, and inventory)
    document.getElementById('wage').textContent = '$' + state.job_wage + '/turn';
    document.getElementById('rent').textContent = '$' + (state.rent || 0) + '/turn';
    document.getElementById('flat-label').textContent = state.flat_label || 'Homeless';
    document.getElementById('items').textContent = state.items.length > 0
        ? state.items.join(', ')
        : 'None';

    // Track current flat tier for home display
    currentFlatTier = state.flat_tier || 0;

    // Update education section in status panel
    const qualificationLabel = document.getElementById('qualification-label');
    const enrolledCourseLabel = document.getElementById('enrolled-course-label');
    const lectureProgressContainer = document.getElementById('lecture-progress-container');
    const lectureProgress = document.getElementById('lecture-progress');
    const completedCoursesList = document.getElementById('completed-courses-list');

    if (qualificationLabel) {
        qualificationLabel.textContent = state.qualification || 'None';
    }

    if (enrolledCourseLabel) {
        enrolledCourseLabel.textContent = state.enrolled_course ? state.enrolled_course.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Not enrolled';
    }

    if (lectureProgressContainer && lectureProgress) {
        if (state.enrolled_course && state.lectures_completed !== undefined) {
            lectureProgressContainer.style.display = 'flex';
            lectureProgress.textContent = `${state.lectures_completed} lectures completed`;
        } else {
            lectureProgressContainer.style.display = 'none';
        }
    }

    if (completedCoursesList) {
        if (state.completed_courses && state.completed_courses.length > 0) {
            const courseNames = state.completed_courses.map(id =>
                id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            );
            completedCoursesList.textContent = courseNames.join(', ');
        } else {
            completedCoursesList.textContent = 'None';
        }
    }
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
    },
    home: {
        title: 'Your London Flat',
        icon: '🏠',
        description: 'Head home to your cosy London flat. Rest up to reduce tiredness and recover your energy.',
        cost: 'Free',
        npcName: 'Flatmate',
        confirmButtonLabel: 'Rest at home'
    },
    john_lewis: {
        title: 'John Lewis Oxford Street',
        icon: '🏬',
        description: 'Browse the iconic department store for quality clothes and furniture. Items purchased here are kept in your inventory.',
        cost: 'Prices vary by item',
        npcName: 'Sales Assistant',
        confirmButtonLabel: 'Browse products'
    },
    estate_agent: {
        title: 'London Property Partners',
        icon: '🏘️',
        description: 'Find your perfect London home! From budget bedsits to luxury penthouses. Rent is deducted from your money each turn.',
        cost: 'Rent: £10 - £200/turn',
        npcName: 'Estate Agent',
        confirmButtonLabel: 'Browse flats'
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

    // For home action, set dynamic background based on flat tier
    if (action === 'home') {
        const homeImageUrl = HOME_IMAGES[currentFlatTier] || HOME_IMAGES[0];
        modalImage.style.backgroundImage = `url('${homeImageUrl}')`;
    } else {
        modalImage.style.backgroundImage = ''; // Clear inline style, use CSS class
    }

    modalTitle.textContent = details.title;
    modalDescription.textContent = details.description;
    modalCost.textContent = details.cost;
    npcName.textContent = details.npcName;
    confirmBtn.textContent = details.confirmButtonLabel;

    // Show browse buttons for various locations
    const browseBtn = document.getElementById('browse-btn');
    const browseJLBtn = document.getElementById('browse-jl-btn');
    const browseFlatsBtn = document.getElementById('browse-flats-btn');
    const browseCoursesBtn = document.getElementById('browse-courses-btn');
    const browseJobsBtn = document.getElementById('browse-jobs-btn');

    // Hide all browse buttons first
    browseBtn.style.display = 'none';
    browseJLBtn.style.display = 'none';
    browseFlatsBtn.style.display = 'none';
    browseCoursesBtn.style.display = 'none';
    browseJobsBtn.style.display = 'none';

    if (action === 'shop') {
        browseBtn.style.display = 'inline-block';
        confirmBtn.style.display = 'none';
    } else if (action === 'john_lewis') {
        browseJLBtn.style.display = 'inline-block';
        confirmBtn.style.display = 'none';
    } else if (action === 'estate_agent') {
        browseFlatsBtn.style.display = 'inline-block';
        confirmBtn.style.display = 'none';
    } else if (action === 'university') {
        browseCoursesBtn.style.display = 'inline-block';
        confirmBtn.style.display = 'inline-block';
    } else if (action === 'job_office') {
        browseJobsBtn.style.display = 'inline-block';
        confirmBtn.style.display = 'none';
    } else {
        confirmBtn.style.display = 'inline-block';
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
            closeLocationModal();

            // Show eating animation popup, then show success message after user acknowledges
            showEatingPopup(() => {
                showActionMessage(data.message, false);
            });
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

// Browse John Lewis catalogue
async function browseJohnLewis() {
    try {
        const response = await fetch('/api/john_lewis/catalogue');
        const data = await response.json();

        if (data.success) {
            displayJohnLewisCatalogue(data.items);
        } else {
            showActionMessage('Error loading John Lewis catalogue', true);
        }
    } catch (error) {
        showActionMessage('Error loading John Lewis catalogue', true);
        console.error(error);
    }
}

// Display John Lewis catalogue
function displayJohnLewisCatalogue(items) {
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
                    <span class="item-cost">£${item.cost}</span>
                    <span class="item-category">${item.category}</span>
                </div>
            </div>
        `;
        itemCard.onclick = () => purchaseJohnLewisItem(item.name);
        catalogueContainer.appendChild(itemCard);
    });

    // Hide default buttons and show catalogue
    document.querySelector('.modal-buttons').style.display = 'none';
    document.getElementById('shop-catalogue').style.display = 'block';
}

// Purchase a specific John Lewis item
async function purchaseJohnLewisItem(itemName) {
    try {
        const response = await fetch('/api/john_lewis/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_name: itemName })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            updateGameUI(data.state);
            closeLocationModal();
            showActionMessage(data.message, false);
        } else {
            const errorMsg = data.detail || data.message || 'Purchase failed';
            showActionMessage(errorMsg, true);
        }
    } catch (error) {
        showActionMessage('Error purchasing item', true);
        console.error(error);
    }
}

// Browse flats at estate agent
async function browseFlats() {
    try {
        const response = await fetch('/api/estate_agent/catalogue');
        const data = await response.json();

        if (data.success) {
            displayFlatsCatalogue(data.flats);
        } else {
            showActionMessage('Error loading flats catalogue', true);
        }
    } catch (error) {
        showActionMessage('Error loading flats catalogue', true);
        console.error(error);
    }
}

// Display flats catalogue
function displayFlatsCatalogue(flats) {
    const catalogueContainer = document.getElementById('catalogue-items');
    catalogueContainer.innerHTML = '';

    flats.forEach(flat => {
        const flatCard = document.createElement('div');
        flatCard.className = 'catalogue-item flat-item';
        flatCard.innerHTML = `
            <div class="item-emoji">${flat.emoji}</div>
            <div class="item-details">
                <div class="item-name">${flat.name}</div>
                <div class="item-description">${flat.description}</div>
                <div class="item-info">
                    <span class="item-cost rent-cost">£${flat.rent}/turn</span>
                </div>
            </div>
        `;
        flatCard.onclick = () => rentFlat(flat.tier);
        catalogueContainer.appendChild(flatCard);
    });

    // Hide default buttons and show catalogue
    document.querySelector('.modal-buttons').style.display = 'none';
    document.getElementById('shop-catalogue').style.display = 'block';
}

// Rent a specific flat
async function rentFlat(tier) {
    try {
        const response = await fetch('/api/estate_agent/rent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tier: tier })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            updateGameUI(data.state);
            closeLocationModal();
            showActionMessage(data.message, false);
        } else {
            const errorMsg = data.detail || data.message || 'Rental failed';
            showActionMessage(errorMsg, true);
        }
    } catch (error) {
        showActionMessage('Error renting flat', true);
        console.error(error);
    }
}

// Browse university courses
async function browseCourses() {
    try {
        const response = await fetch('/api/university/catalogue');
        const data = await response.json();

        if (data.success) {
            displayCoursesCatalogue(data.courses, data.enrolled_course);
        } else {
            showActionMessage('Error loading course catalogue', true);
        }
    } catch (error) {
        showActionMessage('Error loading course catalogue', true);
        console.error(error);
    }
}

// Display course catalogue
function displayCoursesCatalogue(courses, enrolledCourse) {
    const catalogueContainer = document.getElementById('catalogue-items');
    catalogueContainer.innerHTML = '';

    courses.forEach(course => {
        const courseCard = document.createElement('div');
        courseCard.className = 'catalogue-item course-item';
        if (!course.can_enroll) {
            courseCard.classList.add('locked');
        }

        // Build prerequisites text
        let prereqText = '';
        if (course.missing_prerequisites && course.missing_prerequisites.length > 0) {
            prereqText = `<div class="course-prereqs">Requires: ${course.missing_prerequisites.join(', ')}</div>`;
        }

        // Build jobs unlocked text
        const jobsText = course.jobs_unlocked
            .map(job => `${job[0]} (£${job[1]})`)
            .join(', ');

        courseCard.innerHTML = `
            <div class="item-emoji">${course.emoji}</div>
            <div class="item-details">
                <div class="item-name">${course.name}</div>
                <div class="item-description">${course.description}</div>
                ${prereqText}
                <div class="course-jobs">Unlocks: ${jobsText}</div>
                <div class="item-info">
                    <span class="item-cost">£${course.cost_per_lecture}/lecture</span>
                    <span class="course-lectures">${course.lectures_required} lectures</span>
                </div>
            </div>
        `;

        if (course.can_enroll) {
            courseCard.onclick = () => enrollCourse(course.id);
        }

        catalogueContainer.appendChild(courseCard);
    });

    // Hide default buttons and show catalogue
    document.querySelector('.modal-buttons').style.display = 'none';
    document.getElementById('shop-catalogue').style.display = 'block';
}

// Enroll in a course
async function enrollCourse(courseId) {
    try {
        const response = await fetch('/api/university/enroll', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ course_id: courseId })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            updateGameUI(data.state);
            closeLocationModal();
            showActionMessage(data.message, false);
        } else {
            const errorMsg = data.detail || data.message || 'Enrollment failed';
            showActionMessage(errorMsg, true);
        }
    } catch (error) {
        showActionMessage('Error enrolling in course', true);
        console.error(error);
    }
}

// Browse jobs at job office
async function browseJobs() {
    try {
        const response = await fetch('/api/job_office/jobs');
        const data = await response.json();

        if (data.success) {
            displayJobsCatalogue(data.jobs, data.current_job);
        } else {
            showActionMessage('Error loading jobs', true);
        }
    } catch (error) {
        showActionMessage('Error loading jobs', true);
        console.error(error);
    }
}

// Display jobs catalogue
function displayJobsCatalogue(jobs, currentJob) {
    const catalogueContainer = document.getElementById('catalogue-items');
    catalogueContainer.innerHTML = '';

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'catalogue-item job-item';
        if (job.title === currentJob) {
            jobCard.classList.add('current-job');
        }

        jobCard.innerHTML = `
            <div class="item-emoji">💼</div>
            <div class="item-details">
                <div class="item-name">${job.title}${job.title === currentJob ? ' (Current)' : ''}</div>
                <div class="item-info">
                    <span class="item-cost job-wage">£${job.wage}/turn</span>
                </div>
            </div>
        `;

        if (job.title !== currentJob && job.title !== 'Unemployed') {
            jobCard.onclick = () => applyForJob(job.title);
        }

        catalogueContainer.appendChild(jobCard);
    });

    // Hide default buttons and show catalogue
    document.querySelector('.modal-buttons').style.display = 'none';
    document.getElementById('shop-catalogue').style.display = 'block';
}

// Apply for a job
async function applyForJob(jobTitle) {
    try {
        const response = await fetch('/api/job_office/apply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ job_title: jobTitle })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            updateGameUI(data.state);
            closeLocationModal();
            showActionMessage(data.message, false);
        } else {
            const errorMsg = data.detail || data.message || 'Application failed';
            showActionMessage(errorMsg, true);
        }
    } catch (error) {
        showActionMessage('Error applying for job', true);
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
