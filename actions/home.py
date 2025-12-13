"""
Home action - handles player rest and recovery
"""
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Rest at home'

# Rest effects
REST_TIREDNESS_REDUCTION = 30
REST_HAPPINESS_BOOST = 5


@log_function_call
def visit_home(state):
    """
    Player goes home to rest and recover

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    old_tiredness = state.get('tiredness', 0)
    old_happiness = state.get('happiness', 50)

    # Reduce tiredness
    new_tiredness = max(0, old_tiredness - REST_TIREDNESS_REDUCTION)
    state['tiredness'] = new_tiredness
    tiredness_reduced = old_tiredness - new_tiredness

    # Slight happiness boost from resting
    new_happiness = min(100, old_happiness + REST_HAPPINESS_BOOST)
    state['happiness'] = new_happiness

    message = "You rested at home. Tiredness reduced by {}! Feeling a bit happier.".format(
        tiredness_reduced
    )
    return state, message, True
