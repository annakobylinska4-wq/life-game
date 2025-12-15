"""
Home action - handles player rest and recovery
"""
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Rest at home'

# Rest effects based on flat tier (0-5)
# Better homes provide better rest and happiness bonuses
# Values scaled for 2h rest period (1/4 of original 8h values)
REST_BENEFITS = {
    0: {'tiredness_reduction': 4, 'happiness_boost': 0, 'description': 'rough night on the streets'},
    1: {'tiredness_reduction': 5, 'happiness_boost': 1, 'description': 'dingy bedsit'},
    2: {'tiredness_reduction': 8, 'happiness_boost': 1, 'description': 'basic studio'},
    3: {'tiredness_reduction': 10, 'happiness_boost': 3, 'description': 'comfortable flat'},
    4: {'tiredness_reduction': 13, 'happiness_boost': 4, 'description': 'stylish apartment'},
    5: {'tiredness_reduction': 15, 'happiness_boost': 5, 'description': 'luxury penthouse'},
}


@log_function_call
def visit_home(state):
    """
    Player goes home to rest and recover.
    Better flats provide more tiredness reduction and happiness boost.

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    old_tiredness = state.get('tiredness', 0)
    old_happiness = state.get('happiness', 50)
    flat_tier = state.get('flat_tier', 0)

    # Get rest benefits based on flat tier
    benefits = REST_BENEFITS.get(flat_tier, REST_BENEFITS[0])
    tiredness_reduction = benefits['tiredness_reduction']
    happiness_boost = benefits['happiness_boost']
    description = benefits['description']

    # Reduce tiredness
    new_tiredness = max(0, old_tiredness - tiredness_reduction)
    state['tiredness'] = new_tiredness
    tiredness_reduced = old_tiredness - new_tiredness

    # Happiness boost from resting (better homes = more happiness)
    new_happiness = min(100, old_happiness + happiness_boost)
    state['happiness'] = new_happiness
    happiness_gained = new_happiness - old_happiness

    # Build message based on flat tier
    if flat_tier == 0:
        message = f"You found a spot to sleep rough. Tiredness reduced by {tiredness_reduced}."
    elif happiness_gained > 0:
        message = f"You rested in your {description}. Tiredness reduced by {tiredness_reduced}! Happiness +{happiness_gained}."
    else:
        message = f"You rested in your {description}. Tiredness reduced by {tiredness_reduced}."

    return state, message, True
