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
