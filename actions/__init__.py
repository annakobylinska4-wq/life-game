"""
Actions library - handles all player actions in the game
"""
from .university import visit_university, BUTTON_LABEL as UNIVERSITY_BUTTON_LABEL
from .job_office import visit_job_office, BUTTON_LABEL as JOB_OFFICE_BUTTON_LABEL
from .workplace import visit_workplace, BUTTON_LABEL as WORKPLACE_BUTTON_LABEL
from .shop import visit_shop, BUTTON_LABEL as SHOP_BUTTON_LABEL
from .home import visit_home, BUTTON_LABEL as HOME_BUTTON_LABEL
from .john_lewis import visit_john_lewis, BUTTON_LABEL as JOHN_LEWIS_BUTTON_LABEL
from .estate_agent import visit_estate_agent, BUTTON_LABEL as ESTATE_AGENT_BUTTON_LABEL


# Action registry - maps action names to their handler functions
ACTION_HANDLERS = {
    'university': visit_university,
    'job_office': visit_job_office,
    'workplace': visit_workplace,
    'shop': visit_shop,
    'home': visit_home,
    'john_lewis': visit_john_lewis,
    'estate_agent': visit_estate_agent
}

# Button labels for each action - used by frontend to display context-specific labels
ACTION_BUTTON_LABELS = {
    'university': UNIVERSITY_BUTTON_LABEL,
    'job_office': JOB_OFFICE_BUTTON_LABEL,
    'workplace': WORKPLACE_BUTTON_LABEL,
    'shop': SHOP_BUTTON_LABEL,
    'home': HOME_BUTTON_LABEL,
    'john_lewis': JOHN_LEWIS_BUTTON_LABEL,
    'estate_agent': ESTATE_AGENT_BUTTON_LABEL
}


def get_action_type_for_location(location):
    """
    Map location to action type for time calculations.

    Most locations use their name as the action type, with a few exceptions:
    - home -> rest
    - workplace -> work
    - shop -> shop_purchase

    Args:
        location: Location name

    Returns:
        str: Action type for time cost calculations
    """
    location_to_action = {
        'home': 'rest',
        'workplace': 'work',
        'shop': 'shop_purchase',
    }
    return location_to_action.get(location, location)


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


__all__ = [
    'visit_university',
    'visit_job_office',
    'visit_workplace',
    'visit_shop',
    'visit_home',
    'visit_john_lewis',
    'visit_estate_agent',
    'perform_action',
    'get_action_type_for_location',
    'ACTION_HANDLERS',
    'ACTION_BUTTON_LABELS'
]
