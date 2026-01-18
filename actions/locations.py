"""
Location metadata and utilities for game locations.

This module centralizes all location-related metadata including:
- Opening hours
- Display names
- Location availability checks
"""

# Import all Action classes to access their metadata
from actions.home import HomeAction
from actions.workplace import WorkplaceAction
from actions.university import UniversityAction
from actions.shop import ShopAction
from actions.john_lewis import JohnLewisAction
from actions.job_office import JobOfficeAction
from actions.estate_agent import EstateAgentAction


# Map location names to their Action classes
LOCATION_ACTION_CLASSES = {
    'home': HomeAction,
    'workplace': WorkplaceAction,
    'university': UniversityAction,
    'shop': ShopAction,
    'john_lewis': JohnLewisAction,
    'job_office': JobOfficeAction,
    'estate_agent': EstateAgentAction
}


def get_location_display_name(location):
    """
    Get the display name for a location.

    Args:
        location: Location identifier

    Returns:
        str: Display name for the location
    """
    action_class = LOCATION_ACTION_CLASSES.get(location)
    if not action_class:
        return 'This location'
    return action_class.LOCATION_DISPLAY_NAME


def is_location_open(location, minutes_remaining):
    """
    Check if a location is open based on current time.

    Args:
        location: Location name
        minutes_remaining: Minutes left in the day

    Returns:
        tuple: (is_open, opening_hour, closing_hour) or (True, None, None) if no hours
    """
    from models.game_state import format_time

    action_class = LOCATION_ACTION_CLASSES.get(location)
    if not action_class:
        return True, None, None

    opening_hours = action_class.LOCATION_OPENING_HOURS
    if not opening_hours:
        return True, None, None

    open_hour, close_hour = opening_hours
    time_str = format_time(minutes_remaining)
    current_hour = int(time_str.split(':')[0])

    is_open = open_hour <= current_hour < close_hour
    return is_open, open_hour, close_hour


def get_location_opening_hours(location):
    """
    Get the opening hours for a location.

    Args:
        location: Location identifier

    Returns:
        tuple: (open_hour, close_hour) or None if always open
    """
    action_class = LOCATION_ACTION_CLASSES.get(location)
    if not action_class:
        return None
    return action_class.LOCATION_OPENING_HOURS
