"""
Actions library - handles all player actions in the game
"""
from .university import visit_university, BUTTON_LABEL as UNIVERSITY_BUTTON_LABEL
from .job_office import visit_job_office, BUTTON_LABEL as JOB_OFFICE_BUTTON_LABEL
from .workplace import visit_workplace, BUTTON_LABEL as WORKPLACE_BUTTON_LABEL
from .shop import visit_shop, BUTTON_LABEL as SHOP_BUTTON_LABEL


# Action registry - maps action names to their handler functions
ACTION_HANDLERS = {
    'university': visit_university,
    'job_office': visit_job_office,
    'workplace': visit_workplace,
    'shop': visit_shop
}

# Button labels for each action - used by frontend to display context-specific labels
ACTION_BUTTON_LABELS = {
    'university': UNIVERSITY_BUTTON_LABEL,
    'job_office': JOB_OFFICE_BUTTON_LABEL,
    'workplace': WORKPLACE_BUTTON_LABEL,
    'shop': SHOP_BUTTON_LABEL
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
    'ACTION_HANDLERS',
    'ACTION_BUTTON_LABELS'
]
