"""
Actions library - handles all player actions in the game
"""
from .university import visit_university
from .job_office import visit_job_office
from .workplace import visit_workplace
from .shop import visit_shop


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


__all__ = [
    'visit_university',
    'visit_job_office',
    'visit_workplace',
    'visit_shop',
    'perform_action',
    'ACTION_HANDLERS'
]
