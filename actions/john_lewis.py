"""
John Lewis action - handles clothes and furniture purchases
Items are stored in inventory for later use
"""
import random
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Browse products'


# John Lewis catalogue - work clothes only (stored in inventory)
JOHN_LEWIS_ITEMS = [
    {'name': 'Formal Suit', 'cost': 250, 'category': 'workwear', 'emoji': '🤵'},
    {'name': 'Blazer', 'cost': 180, 'category': 'workwear', 'emoji': '🧥'},
    {'name': 'Dress Shirt', 'cost': 65, 'category': 'workwear', 'emoji': '👔'},
    {'name': 'Oxford Shirt', 'cost': 55, 'category': 'workwear', 'emoji': '👔'},
    {'name': 'Dress Trousers', 'cost': 90, 'category': 'workwear', 'emoji': '👖'},
    {'name': 'Chinos', 'cost': 70, 'category': 'workwear', 'emoji': '👖'},
    {'name': 'Oxford Shoes', 'cost': 140, 'category': 'workwear', 'emoji': '👞'},
    {'name': 'Brogues', 'cost': 160, 'category': 'workwear', 'emoji': '👞'},
    {'name': 'Silk Tie', 'cost': 55, 'category': 'workwear', 'emoji': '👔'},
    {'name': 'Leather Belt', 'cost': 45, 'category': 'workwear', 'emoji': '🩹'},
    {'name': 'Waistcoat', 'cost': 95, 'category': 'workwear', 'emoji': '🦺'},
    {'name': 'Cufflinks', 'cost': 40, 'category': 'workwear', 'emoji': '🔘'},
]


@log_function_call
def get_john_lewis_catalogue():
    """
    Get the full John Lewis catalogue

    Returns:
        list: List of all available items with their details
    """
    return JOHN_LEWIS_ITEMS


@log_function_call
def visit_john_lewis(state):
    """
    Player visits John Lewis to browse (random purchase for backward compatibility)

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Buy a random affordable item
    affordable = [item for item in JOHN_LEWIS_ITEMS if item['cost'] <= state['money']]

    if not affordable:
        return state, 'Not enough money to buy anything at John Lewis!', False

    item = random.choice(affordable)
    state['money'] -= item['cost']
    state['items'].append(item['name'])

    # Shopping boosts happiness
    happiness_boost = 10
    state['happiness'] = min(100, state.get('happiness', 50) + happiness_boost)

    message = "You bought {} for £{}! It's now in your inventory. Happiness +{}!".format(
        item['name'], item['cost'], happiness_boost
    )
    return state, message, True


@log_function_call
def purchase_john_lewis_item(state, item_name):
    """
    Purchase a specific item from John Lewis

    Args:
        state: Current game state dictionary
        item_name: Name of the item to purchase

    Returns:
        tuple: (updated_state, message, success)
    """
    # Find the item
    item = next((i for i in JOHN_LEWIS_ITEMS if i['name'] == item_name), None)

    if not item:
        return state, 'Item not found!', False

    if state['money'] < item['cost']:
        return state, 'Not enough money to buy {}!'.format(item['name']), False

    # Purchase the item (stored in inventory, unlike food)
    state['money'] -= item['cost']
    state['items'].append(item['name'])

    # Shopping boosts happiness
    happiness_boost = 10
    state['happiness'] = min(100, state.get('happiness', 50) + happiness_boost)

    message = "You bought {} for £{}! It's now in your inventory. Happiness +{}!".format(
        item['name'], item['cost'], happiness_boost
    )
    return state, message, True
