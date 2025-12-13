"""
Estate Agent action - handles flat rentals for players
"""
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Browse flats'

# Flat tiers with rent prices and descriptions
# Tier 0 = homeless (no flat), Tier 1-5 = increasingly nicer flats
FLAT_CATALOGUE = [
    {
        'tier': 1,
        'name': 'Dingy Bedsit',
        'rent': 10,
        'description': 'A cramped, damp bedsit with peeling wallpaper and a shared bathroom down the hall.',
        'emoji': '🏚️'
    },
    {
        'tier': 2,
        'name': 'Basic Studio',
        'rent': 25,
        'description': 'A small but functional studio flat. Nothing fancy, but it keeps the rain out.',
        'emoji': '🏢'
    },
    {
        'tier': 3,
        'name': 'Comfortable Flat',
        'rent': 50,
        'description': 'A decent one-bedroom flat with modern amenities and a proper kitchen.',
        'emoji': '🏠'
    },
    {
        'tier': 4,
        'name': 'Stylish Apartment',
        'rent': 100,
        'description': 'A spacious two-bedroom apartment with high ceilings and quality furnishings.',
        'emoji': '🏡'
    },
    {
        'tier': 5,
        'name': 'Luxury Penthouse',
        'rent': 200,
        'description': 'An exquisite penthouse with panoramic city views, designer interiors, and a private terrace.',
        'emoji': '🏰'
    }
]

# Flat tier labels for display
FLAT_TIER_LABELS = {
    0: 'Homeless',
    1: 'Dingy Bedsit',
    2: 'Basic Studio',
    3: 'Comfortable Flat',
    4: 'Stylish Apartment',
    5: 'Luxury Penthouse'
}


def get_flat_catalogue():
    """
    Get the list of available flats for rent.

    Returns:
        list: List of flat dictionaries
    """
    return FLAT_CATALOGUE


def get_flat_by_tier(tier):
    """
    Get flat details by tier number.

    Args:
        tier: Flat tier (1-5)

    Returns:
        dict: Flat details or None if not found
    """
    for flat in FLAT_CATALOGUE:
        if flat['tier'] == tier:
            return flat
    return None


def get_flat_label(tier):
    """
    Get human-readable label for flat tier.

    Args:
        tier: Flat tier (0-5)

    Returns:
        str: Human-readable flat label
    """
    return FLAT_TIER_LABELS.get(tier, 'Homeless')


@log_function_call
def visit_estate_agent(state):
    """
    Player visits the estate agent to view available flats.
    This is a browsing action - actual rental is done via rent_flat.

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    current_tier = state.get('flat_tier', 0)
    current_rent = state.get('rent', 0)

    if current_tier == 0:
        message = "Welcome! You're currently homeless. Browse our selection of flats to find your new home."
    else:
        flat = get_flat_by_tier(current_tier)
        flat_name = flat['name'] if flat else 'Unknown'
        message = f"Welcome back! You're currently renting a {flat_name} for £{current_rent}/turn. Looking to upgrade?"

    return state, message, True


@log_function_call
def rent_flat(state, tier):
    """
    Rent a flat of the specified tier.

    Args:
        state: Current game state dictionary
        tier: Flat tier to rent (1-5)

    Returns:
        tuple: (updated_state, message, success)
    """
    flat = get_flat_by_tier(tier)

    if not flat:
        return state, "Invalid flat selection.", False

    current_tier = state.get('flat_tier', 0)

    # Check if already renting the same flat
    if current_tier == tier:
        return state, f"You're already renting a {flat['name']}!", False

    # Update state with new flat
    state['flat_tier'] = tier
    state['rent'] = flat['rent']

    if current_tier == 0:
        message = f"Congratulations! You've rented a {flat['name']} for £{flat['rent']}/turn. No more sleeping rough!"
    elif tier > current_tier:
        message = f"Moving up in the world! You've upgraded to a {flat['name']} for £{flat['rent']}/turn."
    else:
        message = f"You've downgraded to a {flat['name']} for £{flat['rent']}/turn. Every penny counts!"

    return state, message, True
