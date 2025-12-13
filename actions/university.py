"""
University action - handles player education
"""
from config import config
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Attend lecture'


@log_function_call
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

    # Different degree types, each divided into parts
    qualifications = [
        'None',
        'High School',
        'Bachelor - Part 1',
        'Bachelor - Part 2',
        'Bachelor - Part 3',
        'Master - Part 1',
        'Master - Part 2',
        'Master - Part 3',
        'PhD - Part 1',
        'PhD - Part 2',
        'PhD - Part 3'
    ]

    degree_names = {
        'Bachelor - Part 1': 'Bachelor of Science - Part 1',
        'Bachelor - Part 2': 'Bachelor of Science - Part 2',
        'Bachelor - Part 3': 'Bachelor of Science - Part 3',
        'Master - Part 1': 'Master of Business Administration - Part 1',
        'Master - Part 2': 'Master of Business Administration - Part 2',
        'Master - Part 3': 'Master of Business Administration - Part 3',
        'PhD - Part 1': 'Doctor of Philosophy - Part 1',
        'PhD - Part 2': 'Doctor of Philosophy - Part 2',
        'PhD - Part 3': 'Doctor of Philosophy - Part 3'
    }

    current_idx = qualifications.index(state['qualification'])

    if current_idx < len(qualifications) - 1:
        state['qualification'] = qualifications[current_idx + 1]
        display_name = degree_names.get(state['qualification'], state['qualification'])
        message = "You studied hard and completed: {} (-${})".format(
            display_name, cost
        )
    else:
        message = "You are already at the highest qualification level!"
        state['money'] += cost  # Refund

    return state, message, True
