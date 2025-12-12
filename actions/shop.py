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
    # Food items: (name, cost, calories)
    items_available = [
        ('Apple', 3, 95),
        ('Banana', 2, 105),
        ('Bread', 5, 265),
        ('Milk', 4, 150),
        ('Eggs', 6, 155),
        ('Cheese', 8, 200),
        ('Chicken', 12, 335),
        ('Beef', 15, 425),
        ('Rice', 7, 205),
        ('Pasta', 6, 220),
        ('Vegetables', 10, 120),
        ('Pizza', 14, 285),
        ('Sandwich', 9, 250),
        ('Coffee', 5, 95),
        ('Chocolate', 4, 210)
    ]

    # Buy a random affordable item
    affordable = [item for item in items_available if item[1] <= state['money']]

    if not affordable:
        return state, 'Not enough money to buy anything!', False

    item_name, item_cost, calories = random.choice(affordable)
    state['money'] -= item_cost
    state['items'].append(item_name)

    # Reduce hunger based on calories (higher calories = more hunger reduction)
    hunger_reduction = min(calories // 10, state['hunger'])  # Each 10 calories reduces 1 hunger point
    state['hunger'] = max(0, state['hunger'] - hunger_reduction)

    message = "You bought {} for ${} ({} calories). Hunger reduced by {}!".format(
        item_name, item_cost, calories, hunger_reduction
    )
    return state, message, True
