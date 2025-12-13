"""
Workplace action - handles player work and earnings
"""
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Work'

# Working increases tiredness
WORK_TIREDNESS_INCREASE = 20


@log_function_call
def visit_workplace(state):
    """
    Player goes to work and earns money

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    if state['current_job'] == 'Unemployed':
        return state, 'You need to get a job first!', False

    earnings = state['job_wage']
    state['money'] += earnings

    # Increase tiredness from working
    old_tiredness = state.get('tiredness', 0)
    new_tiredness = min(100, old_tiredness + WORK_TIREDNESS_INCREASE)
    state['tiredness'] = new_tiredness

    message = "You worked as {} and earned ${}. You feel a bit more tired.".format(state['current_job'], earnings)
    return state, message, True
