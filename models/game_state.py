"""
GameState class for managing player game state
"""
from config.config import config


# Time constants (in minutes)
MINUTES_PER_DAY = 1440  # 24 hours
DAY_START_HOUR = 6  # Day starts at 6:00 AM

# Action time costs (in minutes)
ACTION_TIME_COSTS = 120
TRAVEL_TIME = 60

def format_time(minutes_remaining):
    """
    Convert minutes remaining in day to 24-hour clock time.
    Day starts at 6:00 AM (360 minutes into midnight).

    Args:
        minutes_remaining: Minutes left in the day

    Returns:
        str: Time in HH:MM format
    """
    # Minutes used = total - remaining
    minutes_used = MINUTES_PER_DAY - minutes_remaining

    # Add to 6:00 AM start
    total_minutes = (DAY_START_HOUR * 60) + minutes_used

    # Wrap around midnight if needed
    total_minutes = total_minutes % 1440

    hours = total_minutes // 60
    mins = total_minutes % 60

    return f"{hours:02d}:{mins:02d}"


def get_time_period(minutes_remaining):
    """
    Get the period of day based on time.

    Returns:
        str: 'morning', 'afternoon', 'evening', or 'night'
    """
    time_str = format_time(minutes_remaining)
    hour = int(time_str.split(':')[0])

    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'


# Opening hours and display names are now stored in Action classes
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


# Flat tier labels (0-5 scale, 0 = homeless)
FLAT_TIER_LABELS = {
    0: 'Homeless',
    1: 'Dingy Bedsit',
    2: 'Basic Studio',
    3: 'Comfortable Flat',
    4: 'Stylish Apartment',
    5: 'Luxury Penthouse'
}


def get_flat_label(flat_tier):
    """
    Get human-readable label for flat tier.

    Args:
        flat_tier: Flat tier value (0-5)

    Returns:
        str: Human-readable flat tier label
    """
    return FLAT_TIER_LABELS.get(flat_tier, 'Homeless')


# Look level labels (1-5 scale)
LOOK_LABELS = {
    1: 'Shabby',
    2: 'Scruffy',
    3: 'Presentable',
    4: 'Smart',
    5: 'Very well groomed'
}

# Tiredness level labels (based on 0-100 scale)
# Lower values = well rested, higher values = exhausted
TIREDNESS_LABELS = [
    (0, 20, 'Well rested'),
    (21, 40, 'Slightly tired'),
    (41, 60, 'Tired'),
    (61, 80, 'Very tired'),
    (81, 100, 'Exhausted')
]

# Happiness level labels (based on 0-100 scale)
# Higher values = happier
HAPPINESS_LABELS = [
    (0, 20, 'Miserable'),
    (21, 40, 'Unhappy'),
    (41, 60, 'Content'),
    (61, 80, 'Happy'),
    (81, 100, 'Ecstatic')
]

# Hunger level labels (based on 0-100 scale)
# Lower values = well fed, higher values = starving
HUNGER_LABELS = [
    (0, 20, 'Full'),
    (21, 40, 'Satisfied'),
    (41, 60, 'Peckish'),
    (61, 80, 'Hungry'),
    (81, 100, 'Starving')
]


def get_tiredness_label(tiredness_value):
    """
    Get human-readable label for tiredness level.

    Args:
        tiredness_value: Tiredness value (0-100)

    Returns:
        str: Human-readable tiredness label
    """
    for min_val, max_val, label in TIREDNESS_LABELS:
        if min_val <= tiredness_value <= max_val:
            return label
    return 'Exhausted'  # Default for values > 100


def get_happiness_label(happiness_value):
    """
    Get human-readable label for happiness level.

    Args:
        happiness_value: Happiness value (0-100)

    Returns:
        str: Human-readable happiness label
    """
    for min_val, max_val, label in HAPPINESS_LABELS:
        if min_val <= happiness_value <= max_val:
            return label
    return 'Miserable'  # Default for values < 0


def get_hunger_label(hunger_value):
    """
    Get human-readable label for hunger level.

    Args:
        hunger_value: Hunger value (0-100)

    Returns:
        str: Human-readable hunger label
    """
    for min_val, max_val, label in HUNGER_LABELS:
        if min_val <= hunger_value <= max_val:
            return label
    return 'Starving'  # Default for values > 100


class GameState:
    """
    Represents a player's game state with all tracked features.
    This class encapsulates all game state logic in one place.
    """

    def __init__(self, state_dict=None):
        """
        Initialize a game state from a dictionary or create a new one.

        Args:
            state_dict (dict, optional): Existing state data. If None, creates new game state.
        """
        if state_dict:
            # Load from existing state
            self.money = state_dict.get('money', config.INITIAL_MONEY)
            self.items = state_dict.get('items', [])
            self.qualification = state_dict.get('qualification', 'None')
            self.current_job = state_dict.get('current_job', 'Unemployed')
            self.job_wage = state_dict.get('job_wage', 0)
            self.happiness = state_dict.get('happiness', config.INITIAL_HAPPINESS)
            self.tiredness = state_dict.get('tiredness', config.INITIAL_TIREDNESS)
            self.hunger = state_dict.get('hunger', config.INITIAL_HUNGER)
            self.look = state_dict.get('look', 1)
            self.flat_tier = state_dict.get('flat_tier', 0)  # 0 = homeless
            self.rent = state_dict.get('rent', 0)
            # Education state
            self.completed_courses = state_dict.get('completed_courses', [])
            self.enrolled_course = state_dict.get('enrolled_course', None)
            self.lectures_completed = state_dict.get('lectures_completed', 0)
            # Time tracking
            self.turn = state_dict.get('turn', 1)
            self.time_remaining = state_dict.get('time_remaining', MINUTES_PER_DAY)
            self.current_location = state_dict.get('current_location', 'home')
        else:
            # Create new game state with initial values
            self.money = config.INITIAL_MONEY
            self.items = []
            self.qualification = 'None'
            self.current_job = 'Unemployed'
            self.job_wage = 0
            self.happiness = config.INITIAL_HAPPINESS
            self.tiredness = config.INITIAL_TIREDNESS
            self.hunger = config.INITIAL_HUNGER
            self.look = 1  # Start at level 1 (Shabby)
            self.flat_tier = 0  # Start homeless
            self.rent = 0  # No rent when homeless
            # Education state
            self.completed_courses = []
            self.enrolled_course = None
            self.lectures_completed = 0
            # Time tracking
            self.turn = 1
            self.time_remaining = MINUTES_PER_DAY  # time remaining in this turn
            self.current_location = 'home'  # Start at home

    def to_dict(self):
        """
        Convert the game state to a dictionary for serialization.

        Returns:
            dict: Dictionary representation of the game state
        """
        return {
            'money': self.money,
            'items': self.items,
            'qualification': self.qualification,
            'current_job': self.current_job,
            'job_wage': self.job_wage,
            'turn': self.turn,
            'happiness': self.happiness,
            'happiness_label': get_happiness_label(self.happiness),
            'tiredness': self.tiredness,
            'tiredness_label': get_tiredness_label(self.tiredness),
            'hunger': self.hunger,
            'hunger_label': get_hunger_label(self.hunger),
            'look': self.look,
            'look_label': LOOK_LABELS.get(self.look, 'Shabby'),
            'flat_tier': self.flat_tier,
            'flat_label': get_flat_label(self.flat_tier),
            'rent': self.rent,
            'completed_courses': self.completed_courses,
            'enrolled_course': self.enrolled_course,
            'lectures_completed': self.lectures_completed,
            # Time tracking
            'time_remaining': self.time_remaining,
            'current_time': format_time(self.time_remaining),
            'time_period': get_time_period(self.time_remaining),
            'current_location': self.current_location
        }

    @classmethod
    def create_new(cls):
        """
        Factory method to create a new game state.

        Returns:
            GameState: A new game state with initial values
        """
        return cls()

    def increment_turn(self):
        """
        Increment the turn counter and apply per-turn updates.

        Returns:
            dict: Summary of changes that occurred during turn increment
        """
        old_turn = self.turn
        old_hunger = self.hunger
        old_money = self.money

        self.turn += 1
        self._apply_turn_updates()

        # Reset time for new day
        self.time_remaining = MINUTES_PER_DAY
        self.current_location = 'home'  # Wake up at home

        # Build turn summary
        changes = []

        # Hunger change
        hunger_increase = self.hunger - old_hunger
        if hunger_increase > 0:
            changes.append({
                'type': 'hunger',
                'icon': '🍽️',
                'text': f'You got hungrier (+{hunger_increase} hunger)',
                'class': 'change-negative'
            })

        # Rent deduction
        if self.rent > 0:
            changes.append({
                'type': 'rent',
                'icon': '🏠',
                'text': f'Rent due: -£{self.rent}',
                'class': 'change-negative'
            })

        return {
            'new_day': self.turn,
            'changes': changes,
            'current_status': {
                'money': self.money,
                'hunger': self.hunger,
                'hunger_label': get_hunger_label(self.hunger),
                'tiredness': self.tiredness,
                'tiredness_label': get_tiredness_label(self.tiredness)
            }
        }

    def _apply_turn_updates(self):
        """
        Apply automatic updates that occur each turn.
        Currently includes:
        - Hunger increases by 25 (uncapped, can go arbitrarily high)
        - Rent is deducted from money
        """
        self.hunger += 25
        # Deduct rent each turn
        if self.rent > 0:
            self.money -= self.rent

    def has_enough_time(self):
        """
        Check if there's enough time remaining for travel + action.
        """
        return self.time_remaining >= ACTION_TIME_COSTS + TRAVEL_TIME

    def get_total_time_cost(self):
        """
        Get total time cost for travel and action.

        Returns:
            tuple: (travel_time, action_time, total_time)
        """
        travel_time = TRAVEL_TIME
        action_time = ACTION_TIME_COSTS
        total_time = travel_time + action_time
        return (travel_time, action_time, total_time)

    def spend_time(self, destination, action_type):
        """
        Spend time for travel and action, update location.

        Args:
            destination: Target location
            action_type: Type of action to perform

        Returns:
            tuple: (travel_time, action_time, success, turn_summary)
            turn_summary is None if day didn't end, otherwise contains turn change info
        """
        travel_time, action_time, total_time = (TRAVEL_TIME, ACTION_TIME_COSTS, TRAVEL_TIME + ACTION_TIME_COSTS)

        if self.time_remaining < total_time:
            return (travel_time, action_time, False, None)

        self.time_remaining -= total_time
        self.current_location = destination

        # Check if day is over (less than 15 minutes remaining)
        turn_summary = None
        if self.time_remaining < 15:
            turn_summary = self.increment_turn()

        return (travel_time, action_time, True, turn_summary)

    def add_money(self, amount):
        """Add money to the player's balance"""
        self.money += amount

    def subtract_money(self, amount):
        """
        Subtract money from the player's balance.

        Returns:
            bool: True if successful, False if insufficient funds
        """
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def add_item(self, item):
        """Add an item to the player's inventory"""
        if item not in self.items:
            self.items.append(item)

    def has_item(self, item):
        """Check if player has a specific item"""
        return item in self.items

    def set_qualification(self, qualification):
        """Set the player's qualification level"""
        self.qualification = qualification

    def set_job(self, job_title, wage):
        """Set the player's current job and wage"""
        self.current_job = job_title
        self.job_wage = wage

    def update_happiness(self, amount):
        """
        Update happiness level (clamped between 0 and 100).

        Args:
            amount: Amount to change happiness by (positive or negative)
        """
        self.happiness = max(0, min(100, self.happiness + amount))

    def update_tiredness(self, amount):
        """
        Update tiredness level (clamped between 0 and 100).

        Args:
            amount: Amount to change tiredness by (positive or negative)
        """
        self.tiredness = max(0, min(100, self.tiredness + amount))

    def update_hunger(self, amount):
        """
        Update hunger level (clamped between 0 and 100).

        Args:
            amount: Amount to change hunger by (positive or negative)
        """
        self.hunger = max(0, min(100, self.hunger + amount))

    def update_look(self):
        """
        Update look level based on clothing items in inventory.
        Look improves as the player acquires more clothing items.
        Scale: 1 (Shabby) to 5 (Very well groomed)
        """
        clothing_count = sum(1 for item in self.items )

        # Calculate look level based on clothing count
        # 0 items = level 1, 2-3 items = level 2, 4-5 items = level 3, etc.
        if clothing_count == 0:
            self.look = 1
        elif clothing_count <= 2:
            self.look = 2
        elif clothing_count <= 4:
            self.look = 3
        elif clothing_count <= 7:
            self.look = 4
        else:
            self.look = 5

    def get_look_label(self):
        """Get the human-readable label for current look level"""
        return LOOK_LABELS.get(self.look, 'Shabby')

    def check_burnout(self):
        """
        Check if player has burned out (exhausted AND starving).
        This triggers a game reset.

        Returns:
            bool: True if player is burned out, False otherwise
        """
        # Exhausted = tiredness >= 81, Starving = hunger >= 81
        is_exhausted = self.tiredness >= 81
        is_starving = self.hunger >= 81
        return is_exhausted and is_starving

    def check_bankruptcy(self):
        """
        Check if player has gone bankrupt (money below 0).
        This triggers a game reset.

        Returns:
            bool: True if player is bankrupt, False otherwise
        """
        return self.money < 0

    def reset(self):
        """
        Reset the game state to initial values.
        Called when player burns out from exhaustion and starvation.
        Preserves the turn count to track total game progress.
        """
        # Preserve turn count
        current_turn = self.turn

        # Reset everything to initial values
        self.money = config.INITIAL_MONEY
        self.items = []
        self.qualification = 'None'
        self.current_job = 'Unemployed'
        self.job_wage = 0
        self.turn = current_turn  # Keep turn count
        self.happiness = config.INITIAL_HAPPINESS
        self.tiredness = config.INITIAL_TIREDNESS
        self.hunger = config.INITIAL_HUNGER
        self.look = 1
        self.flat_tier = 0
        self.rent = 0
        self.completed_courses = []
        self.enrolled_course = None
        self.lectures_completed = 0
        # Reset time tracking
        self.time_remaining = MINUTES_PER_DAY
        self.current_location = 'home'

    def __repr__(self):
        """String representation for debugging"""
        return f"GameState(turn={self.turn}, money={self.money}, job={self.current_job}, happiness={self.happiness}, tiredness={self.tiredness}, hunger={self.hunger}, look={self.look}, flat_tier={self.flat_tier}, rent={self.rent})"
