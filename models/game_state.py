"""
GameState class for managing player game state
"""
from config.config import config


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
            'tiredness': self.tiredness,
            'hunger': self.hunger
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
        """Increment the turn counter"""
        self.turn += 1

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

    def __repr__(self):
        """String representation for debugging"""
        return f"GameState(turn={self.turn}, money={self.money}, job={self.current_job}, happiness={self.happiness}, tiredness={self.tiredness}, hunger={self.hunger})"
