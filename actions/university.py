"""
University action - handles player education
"""
from config import config


def visit_university(state):
    """
    Player visits university to improve qualifications

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    cost = config.UNIVERSITY_COST

    if state['money'] < cost:
        return state, 'Not enough money! Need ${}'.format(cost), False

    state['money'] -= cost
    qualifications = ['None', 'High School', 'Bachelor', 'Master', 'PhD']
    current_idx = qualifications.index(state['qualification'])

    if current_idx < len(qualifications) - 1:
        state['qualification'] = qualifications[current_idx + 1]
        message = "You studied hard and earned a {} degree! (-${})".format(
            state['qualification'], cost
        )
    else:
        message = "You are already at the highest qualification level!"
        state['money'] += cost  # Refund

    return state, message, True
