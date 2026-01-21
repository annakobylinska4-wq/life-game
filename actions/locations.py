"""
Location metadata and utilities for game locations.

This module centralizes all location-related metadata including:
- Opening hours
- Display names
- Location availability checks
"""

# Import location metadata from each module
from actions import home, workplace, university, shop, john_lewis, job_office, estate_agent


# Map location names to their metadata modules
LOCATION_MODULES = {
    'home': home,
    'workplace': workplace,
    'university': university,
    'shop': shop,
    'john_lewis': john_lewis,
    'job_office': job_office,
    'estate_agent': estate_agent
}


def get_location_display_name(location):
    """
    Get the display name for a location.

    Args:
        location: Location identifier

    Returns:
        str: Display name for the location
    """
    module = LOCATION_MODULES.get(location)
    if not module:
        return 'This location'
    return module.LOCATION_DISPLAY_NAME


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

    module = LOCATION_MODULES.get(location)
    if not module:
        return True, None, None

    opening_hours = module.LOCATION_OPENING_HOURS
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
    module = LOCATION_MODULES.get(location)
    if not module:
        return None
    return module.LOCATION_OPENING_HOURS
