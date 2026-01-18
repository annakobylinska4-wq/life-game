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


from .base import Action
from .locations import get_location_display_name, is_location_open, get_location_opening_hours


def check_endgame_conditions(game_state_obj, current_message=None):
    """
    Check for burnout and bankruptcy conditions and reset if needed.

    Note: This is a backward-compatible wrapper. The actual implementation
    is in Action.check_endgame_conditions()
    """
    return Action.check_endgame_conditions(game_state_obj, current_message)


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


def execute_action_with_validation(state, location, action_handler, check_opening_hours=True, post_action_callback=None):
    """
    Generic action execution handler with time and location validation.

    Note: This is a backward-compatible wrapper. The actual implementation
    is in Action.execute_with_validation()
    """
    return Action.execute_with_validation(
        state=state,
        location=location,
        action_handler=action_handler,
        check_opening_hours=check_opening_hours,
        post_action_callback=post_action_callback
    )


__all__ = [
    'visit_university',
    'visit_job_office',
    'visit_workplace',
    'visit_shop',
    'visit_home',
    'visit_john_lewis',
    'visit_estate_agent',
    'perform_action',
    'execute_action_with_validation',
    'check_endgame_conditions',
    'ACTION_HANDLERS',
    'ACTION_BUTTON_LABELS',
    'get_location_display_name',
    'is_location_open',
    'get_location_opening_hours'
]
