"""
Workplace action - handles player work and earnings
"""

# Button label for this action
BUTTON_LABEL = 'Work'


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

    message = "You worked as {} and earned ${}!".format(state['current_job'], earnings)
    return state, message, True
