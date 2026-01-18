"""
Base Action class for all game actions/locations
"""


class Action:
    """
    Base class for all game actions/locations.
    Each action should have a button label, display name, and optional opening hours.
    """

    # Button label shown on the action button
    BUTTON_LABEL = None

    # Display name for the location (used in messages to players)
    LOCATION_DISPLAY_NAME = None

    # Opening hours tuple (open_hour, close_hour) in 24-hour format
    # None means the location is always open
    LOCATION_OPENING_HOURS = None

    def __init__(self):
        """
        Initialize the action instance.
        Subclasses should set the class variables appropriately.
        """
        if self.BUTTON_LABEL is None:
            raise ValueError(f"{self.__class__.__name__} must define BUTTON_LABEL")
        if self.LOCATION_DISPLAY_NAME is None:
            raise ValueError(f"{self.__class__.__name__} must define LOCATION_DISPLAY_NAME")

    @classmethod
    def get_button_label(cls):
        """Get the button label for this action"""
        return cls.BUTTON_LABEL

    @classmethod
    def get_display_name(cls):
        """Get the display name for this location"""
        return cls.LOCATION_DISPLAY_NAME

    @classmethod
    def get_opening_hours(cls):
        """
        Get the opening hours for this location.

        Returns:
            tuple: (open_hour, close_hour) or None if always open
        """
        return cls.LOCATION_OPENING_HOURS

    @staticmethod
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

    @staticmethod
    def execute_with_validation(state, location, action_handler, check_opening_hours=True, post_action_callback=None):
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
        burnout, bankruptcy, message = Action.check_endgame_conditions(game_state_obj, message)

        updated_state = game_state_obj.to_dict()

        return {
            'success': True,
            'state': updated_state,
            'message': message,
            'burnout': burnout,
            'bankruptcy': bankruptcy,
            'turn_summary': turn_summary
        }
