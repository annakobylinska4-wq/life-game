"""
Shop action - handles player purchases
"""
import random


def visit_shop(state):
    """
    Player visits shop to buy items

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    items_available = [
        ('Food', 10),
        ('Clothes', 25),
        ('Phone', 100),
        ('Laptop', 300),
        ('Car', 1000)
    ]

    # Buy a random affordable item
    affordable = [item for item in items_available if item[1] <= state['money']]

    if not affordable:
        return state, 'Not enough money to buy anything!', False

    item_name, item_cost = random.choice(affordable)
    state['money'] -= item_cost
    state['items'].append(item_name)

    message = "You bought {} for ${}!".format(item_name, item_cost)
    return state, message, True
