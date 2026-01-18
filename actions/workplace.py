"""
Workplace action - handles player work and earnings
"""
from utils.function_logger import log_function_call
from .base import Action


class WorkplaceAction(Action):
    """Workplace location for earning money"""
    BUTTON_LABEL = 'Work'
    LOCATION_DISPLAY_NAME = 'Workplace'
    LOCATION_OPENING_HOURS = None  # Always open


# Create instance for backward compatibility
workplace_action = WorkplaceAction()

# Export for backward compatibility
BUTTON_LABEL = WorkplaceAction.BUTTON_LABEL

# Working increases tiredness (scaled for 2h work period, 1/4 of original 8h value)
WORK_TIREDNESS_INCREASE = 5


@log_function_call
def visit_workplace(state):
    """
    Player goes to work and earns money.
    Earnings are scaled for 2h work period (1/4 of full day wage).

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    if state['current_job'] == 'Unemployed':
        return state, 'You need to get a job first!', False

    # Scale earnings for 2h work period (1/4 of full day wage)
    full_wage = state['job_wage']
    earnings = full_wage // 4
    state['money'] += earnings

    # Increase tiredness from working
    old_tiredness = state.get('tiredness', 0)
    new_tiredness = min(100, old_tiredness + WORK_TIREDNESS_INCREASE)
    state['tiredness'] = new_tiredness

    message = "You worked as {} and earned £{}. You feel a bit more tired.".format(state['current_job'], earnings)
    return state, message, True
