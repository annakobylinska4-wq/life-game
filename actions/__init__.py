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


def check_endgame_conditions(game_state_obj, current_message=None):
    """
    Check for burnout and bankruptcy conditions and reset if needed.

    Args:
        game_state_obj: GameState instance to check
        current_message: Optional message to override if endgame condition is met

    Returns:
        tuple: (burnout, bankruptcy, message)
    """
    burnout = game_state_obj.check_burnout()
    if burnout:
        game_state_obj.reset()
        message = "BURNOUT"
    else:
        message = current_message

    bankruptcy = game_state_obj.check_bankruptcy()
    if bankruptcy:
        game_state_obj.reset()
        message = "BANKRUPTCY"

    return burnout, bankruptcy, message


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


def execute_action_with_validation(
    state,
    location,
    action_handler,
    check_opening_hours=True,
    post_action_callback=None
):
    """
    Generic action execution handler with time and location validation.

    This centralizes all the common logic for:
    - Checking if player has enough time
    - Checking if location is open
    - Spending time for travel and action
    - Executing the action
    - Handling endgame conditions

    Args:
        state: Current game state dictionary
        location: Location identifier (e.g., 'shop', 'john_lewis', 'job_office', 'university')
        action_handler: Function to execute the actual action, should return (updated_state, message, success)
        check_opening_hours: Whether to check if location is open (default True)
        post_action_callback: Optional callback to run after action (e.g., update_look for clothing)

    Returns:
        dict: Result with keys:
            - success: bool
            - state: updated game state dict
            - message: str
            - burnout: bool
            - bankruptcy: bool
            - turn_summary: dict or None
            - error: str (only if validation failed)
    """
    from models import GameState
    from models.game_state import is_location_open, get_location_display_name

    # Create GameState object for validation
    game_state_obj = GameState(state)

    # Check if location is open
    if check_opening_hours:
        is_open, open_hour, close_hour = is_location_open(location, game_state_obj.time_remaining)
        if not is_open:
            location_name = get_location_display_name(location)
            return {
                'success': False,
                'error': f"{location_name} is closed! Opening hours: {open_hour}am - {close_hour % 12}pm."
            }

    # Check if player has enough time
    if not game_state_obj.has_enough_time():
        travel_time, action_time, total_time = game_state_obj.get_total_time_cost()
        hours = total_time // 60
        mins = total_time % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        return {
            'success': False,
            'error': f"Not enough time today! This would take {time_str} but you only have {game_state_obj.time_remaining // 60}h {game_state_obj.time_remaining % 60}m left."
        }

    # Spend time for travel and action
    travel_time, action_time, _, turn_summary = game_state_obj.spend_time(location)
    state = game_state_obj.to_dict()

    # Execute the actual action
    updated_state, message, success = action_handler(state)

    if not success:
        return {
            'success': False,
            'error': message
        }

    # Use GameState class to handle state
    game_state_obj = GameState(updated_state)

    # Run post-action callback if provided (e.g., update_look for clothing purchases)
    if post_action_callback:
        post_action_callback(game_state_obj)

    # Check for endgame conditions (burnout and bankruptcy)
    burnout, bankruptcy, message = check_endgame_conditions(game_state_obj, message)

    updated_state = game_state_obj.to_dict()

    return {
        'success': True,
        'state': updated_state,
        'message': message,
        'burnout': burnout,
        'bankruptcy': bankruptcy,
        'turn_summary': turn_summary
    }


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
    'ACTION_BUTTON_LABELS'
]
