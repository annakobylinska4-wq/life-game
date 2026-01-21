"""
MCP Tool Definitions for Life Game Actions
Each tool corresponds to a game action that can be triggered via chat
"""
from typing import Any, Dict
from actions import (
    visit_university,
    visit_job_office,
    visit_workplace,
    visit_shop,
    visit_home,
    visit_john_lewis,
    visit_estate_agent
)
from actions.university import enroll_course, get_course_catalogue
from actions.shop import purchase_item, get_shop_catalogue
from actions.john_lewis import purchase_john_lewis_item, get_john_lewis_catalogue
from actions.job_office import apply_for_job, get_available_jobs
from actions.estate_agent import rent_flat, get_flat_catalogue


# Tool definitions for each game action
TOOLS = [
    {
        "name": "attend_lecture",
        "description": "Attend a lecture at university. Requires being enrolled in a course. Each lecture progresses you toward completing your current course.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "enroll_course",
        "description": "Enroll in a university course. Available courses: middle_school, high_school, vocational, bachelor_arts, bachelor_science, bachelor_business, master_arts, master_science, mba, phd, executive_mba. Prerequisites required for advanced courses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "course_id": {
                    "type": "string",
                    "description": "The ID of the course to enroll in (e.g., 'middle_school', 'high_school', 'bachelor_science')"
                }
            },
            "required": ["course_id"]
        }
    },
    {
        "name": "get_job",
        "description": "Visit the job office to automatically get the best available job based on your qualifications and appearance. Better education and appearance unlock higher-paying jobs.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "apply_for_job",
        "description": "Apply for a specific job by title. Requires appropriate education qualifications and appearance level. Higher-paying jobs need better appearance (look level).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "description": "The title of the job to apply for (e.g., 'Junior Developer', 'Marketing Manager')"
                }
            },
            "required": ["job_title"]
        }
    },
    {
        "name": "work",
        "description": "Go to work and earn money based on your current job and wage. Increases tiredness. Requires having a job first.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "buy_food",
        "description": "Buy food from the shop (random affordable item). Food reduces hunger immediately and is not stored in inventory.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "purchase_food_item",
        "description": "Purchase a specific food item from the shop. Items include: Apple, Banana, Bread, Milk, Eggs, Cheese, Chicken, Beef, Rice, Pasta, Vegetables, Pizza, Sandwich, Coffee, Chocolate. Food reduces hunger based on calories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "The name of the food item to purchase (e.g., 'Apple', 'Pizza')"
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "rest",
        "description": "Rest at home to reduce tiredness and recover energy. Better flats provide better rest benefits and happiness boosts.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "browse_john_lewis",
        "description": "Browse John Lewis and buy a random affordable item. Items include work clothes (suits, shirts, shoes) that improve your appearance for job applications.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "purchase_clothing",
        "description": "Purchase a specific clothing item from John Lewis. Available: Formal Suit, Blazer, Dress Shirt, Oxford Shirt, Dress Trousers, Chinos, Oxford Shoes, Brogues, Silk Tie, Leather Belt, Waistcoat, Cufflinks. Better clothes improve your appearance (look level) for jobs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "The name of the clothing item to purchase (e.g., 'Formal Suit', 'Oxford Shoes')"
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "browse_flats",
        "description": "Visit the estate agent to view available flats for rent. Shows your current accommodation and available options.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rent_flat",
        "description": "Rent a flat at the specified tier. Tier 0=Homeless (no rent), Tier 1=Dingy Bedsit (£10/turn), Tier 2=Basic Studio (£25/turn), Tier 3=Comfortable Flat (£50/turn), Tier 4=Stylish Apartment (£100/turn), Tier 5=Luxury Penthouse (£200/turn). Better flats provide better rest.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "integer",
                    "description": "The flat tier to rent (0-5)",
                    "minimum": 0,
                    "maximum": 5
                }
            },
            "required": ["tier"]
        }
    }
]


def execute_tool(tool_name: str, arguments: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool and return the result

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments with parameters specific to each tool
        game_state: Current game state

    Returns:
        Dict containing:
            - success: bool
            - message: str
            - updated_state: dict (if success)
    """
    # Simple tool handlers (no arguments)
    simple_handlers = {
        'attend_lecture': visit_university,
        'get_job': visit_job_office,
        'work': visit_workplace,
        'buy_food': visit_shop,
        'rest': visit_home,
        'browse_john_lewis': visit_john_lewis,
        'browse_flats': visit_estate_agent
    }

    # Parameterized tool handlers (require arguments)
    parameterized_handlers = {
        'enroll_course': lambda state, args: enroll_course(state, args['course_id']),
        'apply_for_job': lambda state, args: apply_for_job(state, args['job_title']),
        'purchase_food_item': lambda state, args: purchase_item(state, args['item_name']),
        'purchase_clothing': lambda state, args: purchase_john_lewis_item(state, args['item_name']),
        'rent_flat': lambda state, args: rent_flat(state, args['tier'])
    }

    # Check simple handlers first
    if tool_name in simple_handlers:
        handler = simple_handlers[tool_name]
        updated_state, message, success = handler(game_state)
    # Check parameterized handlers
    elif tool_name in parameterized_handlers:
        handler = parameterized_handlers[tool_name]
        try:
            updated_state, message, success = handler(game_state, arguments)
        except KeyError as e:
            return {
                'success': False,
                'message': f'Missing required argument: {e}',
                'updated_state': game_state
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error executing tool: {str(e)}',
                'updated_state': game_state
            }
    else:
        return {
            'success': False,
            'message': f'Unknown tool: {tool_name}',
            'updated_state': game_state
        }

    return {
        'success': success,
        'message': message,
        'updated_state': updated_state
    }


def get_tools_for_context(context: str) -> list:
    """
    Get available tools based on the current context/location

    Args:
        context: The current location (university, job_office, workplace, shop, home, john_lewis, estate_agent)

    Returns:
        List of tool definitions available in this context
    """
    context_tools = {
        'university': ['attend_lecture', 'enroll_course'],
        'job_office': ['get_job', 'apply_for_job'],
        'workplace': ['work'],
        'shop': ['buy_food', 'purchase_food_item'],
        'home': ['rest'],
        'john_lewis': ['browse_john_lewis', 'purchase_clothing'],
        'estate_agent': ['browse_flats', 'rent_flat']
    }

    available_tool_names = context_tools.get(context, [])
    return [tool for tool in TOOLS if tool['name'] in available_tool_names]


def get_available_courses_info(game_state: Dict[str, Any]) -> list:
    """
    Get information about available courses for enrollment

    Args:
        game_state: Current game state

    Returns:
        List of available courses with details
    """
    from actions.university import get_available_courses
    completed_courses = game_state.get('completed_courses', [])
    return get_available_courses(completed_courses)


def get_available_jobs_info(game_state: Dict[str, Any]) -> list:
    """
    Get information about available jobs based on education and appearance

    Args:
        game_state: Current game state

    Returns:
        List of available jobs with wage and look requirements
    """
    completed_courses = game_state.get('completed_courses', [])
    current_look = game_state.get('look', 1)
    return get_available_jobs(completed_courses, current_look)


def get_shop_items_info() -> list:
    """
    Get the full catalogue of food items available at the shop

    Returns:
        List of food items with cost, calories, and emoji
    """
    return get_shop_catalogue()


def get_clothing_items_info() -> list:
    """
    Get the full catalogue of clothing items available at John Lewis

    Returns:
        List of clothing items with cost, category, and emoji
    """
    return get_john_lewis_catalogue()


def get_flats_info() -> list:
    """
    Get the full catalogue of flats available for rent

    Returns:
        List of flats with tier, rent, and description
    """
    return get_flat_catalogue()
