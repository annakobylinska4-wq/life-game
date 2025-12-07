"""
Game actions module - handles all player actions in the game
"""
import random
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


def visit_job_office(state):
    """
    Player visits job office to find employment based on qualifications

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Better qualifications = better jobs
    jobs = {
        'None': ('Janitor', 20),
        'High School': ('Cashier', 35),
        'Bachelor': ('Office Worker', 60),
        'Master': ('Manager', 100),
        'PhD': ('Executive', 150)
    }

    job_title, wage = jobs.get(state['qualification'], ('Unemployed', 0))
    state['current_job'] = job_title
    state['job_wage'] = wage

    message = "You secured a job as {} earning ${} per turn!".format(job_title, wage)
    return state, message, True


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


def visit_shop(state):
    """
    Player visits shop to buy items

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    items_available = [
        ('Food', 10),
        ('Clothes', 25),
        ('Phone', 100),
        ('Laptop', 300),
        ('Car', 1000)
    ]

    # Buy a random affordable item
    affordable = [item for item in items_available if item[1] <= state['money']]

    if not affordable:
        return state, 'Not enough money to buy anything!', False

    item_name, item_cost = random.choice(affordable)
    state['money'] -= item_cost
    state['items'].append(item_name)

    message = "You bought {} for ${}!".format(item_name, item_cost)
    return state, message, True


# Action registry - maps action names to their handler functions
ACTION_HANDLERS = {
    'university': visit_university,
    'job_office': visit_job_office,
    'workplace': visit_workplace,
    'shop': visit_shop
}


def perform_action(action_name, state):
    """
    Performs a game action and returns the updated state

    Args:
        action_name: Name of the action to perform
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    handler = ACTION_HANDLERS.get(action_name)

    if not handler:
        return state, 'Invalid action', False

    return handler(state)
