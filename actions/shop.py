"""
Shop action - handles player purchases
"""
import random
from utils.function_logger import log_function_call


# Location metadata
BUTTON_LABEL = 'Buy some food'
LOCATION_DISPLAY_NAME = 'The shop'
LOCATION_OPENING_HOURS = None  # Always open


# Food items catalogue with emoji icons
SHOP_ITEMS = [
    {'name': 'Apple', 'cost': 3, 'calories': 95, 'emoji': '🍎'},
    {'name': 'Banana', 'cost': 2, 'calories': 105, 'emoji': '🍌'},
    {'name': 'Bread', 'cost': 5, 'calories': 265, 'emoji': '🍞'},
    {'name': 'Milk', 'cost': 4, 'calories': 150, 'emoji': '🥛'},
    {'name': 'Eggs', 'cost': 6, 'calories': 155, 'emoji': '🥚'},
    {'name': 'Cheese', 'cost': 8, 'calories': 200, 'emoji': '🧀'},
    {'name': 'Chicken', 'cost': 12, 'calories': 335, 'emoji': '🍗'},
    {'name': 'Beef', 'cost': 15, 'calories': 425, 'emoji': '🥩'},
    {'name': 'Rice', 'cost': 7, 'calories': 205, 'emoji': '🍚'},
    {'name': 'Pasta', 'cost': 6, 'calories': 220, 'emoji': '🍝'},
    {'name': 'Vegetables', 'cost': 10, 'calories': 120, 'emoji': '🥗'},
    {'name': 'Pizza', 'cost': 14, 'calories': 285, 'emoji': '🍕'},
    {'name': 'Sandwich', 'cost': 9, 'calories': 250, 'emoji': '🥪'},
    {'name': 'Coffee', 'cost': 5, 'calories': 95, 'emoji': '☕'},
    {'name': 'Chocolate', 'cost': 4, 'calories': 210, 'emoji': '🍫'}
]


@log_function_call
def get_shop_catalogue():
    """
    Get the full shop catalogue

    Returns:
        list: List of all available items with their details
    """
    return SHOP_ITEMS


@log_function_call
def visit_shop(state):
    """
    Player visits shop to buy items (random mode for backward compatibility)

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Buy a random affordable item
    affordable = [item for item in SHOP_ITEMS if item['cost'] <= state['money']]

    if not affordable:
        return state, 'Not enough money to buy anything!', False

    item = random.choice(affordable)
    state['money'] -= item['cost']
    #state['items'].append(item['name'])

    # Reduce hunger based on calories (higher calories = more hunger reduction)
    hunger_reduction = item['calories'] // 10  # Each 10 calories reduces 1 hunger point
    state['hunger'] = max(0, state['hunger'] - hunger_reduction)

    message = "You bought {} for ${} ({} calories). Hunger reduced by {}!".format(
        item['name'], item['cost'], item['calories'], hunger_reduction
    )
    return state, message, True


@log_function_call
def purchase_item(state, item_name):
    """
    Purchase a specific item from the shop

    Args:
        state: Current game state dictionary
        item_name: Name of the item to purchase

    Returns:
        tuple: (updated_state, message, success)
    """
    # Find the item
    item = next((i for i in SHOP_ITEMS if i['name'] == item_name), None)

    if not item:
        return state, 'Item not found!', False

    if state['money'] < item['cost']:
        return state, 'Not enough money to buy {}!'.format(item['name']), False

    # Purchase the item (food is consumed immediately, not stored in inventory)
    state['money'] -= item['cost']

    # Reduce hunger based on calories
    hunger_reduction = item['calories'] // 10
    state['hunger'] = max(0, state['hunger'] - hunger_reduction)

    message = "You bought {} for ${} ({} calories). Hunger reduced by {}!".format(
        item['name'], item['cost'], item['calories'], hunger_reduction
    )
    return state, message, True
