"""
GameState class for managing player game state
"""
from config.config import config


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

# Clothing items that improve look (from John Lewis)
CLOTHING_ITEMS = [
    'Formal Suit', 'Blazer', 'Dress Shirt', 'Oxford Shirt', 'Dress Trousers',
    'Chinos', 'Oxford Shoes', 'Brogues', 'Silk Tie', 'Leather Belt',
    'Waistcoat', 'Cufflinks', 'Winter Coat', 'Polo Shirt', 'Trainers',
    'Leather Boots', 'Cashmere Jumper', 'Jeans', 'Wool Scarf'
]


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
            self.turn = state_dict.get('turn', 1)
            self.happiness = state_dict.get('happiness', config.INITIAL_HAPPINESS)
            self.tiredness = state_dict.get('tiredness', config.INITIAL_TIREDNESS)
            self.hunger = state_dict.get('hunger', config.INITIAL_HUNGER)
            self.look = state_dict.get('look', 1)
        else:
            # Create new game state with initial values
            self.money = config.INITIAL_MONEY
            self.items = []
            self.qualification = 'None'
            self.current_job = 'Unemployed'
            self.job_wage = 0
            self.turn = 1
            self.happiness = config.INITIAL_HAPPINESS
            self.tiredness = config.INITIAL_TIREDNESS
            self.hunger = config.INITIAL_HUNGER
            self.look = 1  # Start at level 1 (Shabby)

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
            'look_label': LOOK_LABELS.get(self.look, 'Shabby')
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
        """Increment the turn counter and apply per-turn updates"""
        self.turn += 1
        self._apply_turn_updates()

    def _apply_turn_updates(self):
        """
        Apply automatic updates that occur each turn.
        Currently includes:
        - Hunger increases by x (uncapped, can go arbitrarily high)
        """
        self.hunger += 25

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
        clothing_count = sum(1 for item in self.items if item in CLOTHING_ITEMS)

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

    def __repr__(self):
        """String representation for debugging"""
        return f"GameState(turn={self.turn}, money={self.money}, job={self.current_job}, happiness={self.happiness}, tiredness={self.tiredness}, hunger={self.hunger}, look={self.look})"
