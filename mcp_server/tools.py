"""
MCP Tool Definitions for Life Game Actions
Each tool corresponds to a game action that can be triggered via chat
"""
from typing import Any, Dict
from actions import visit_university, visit_job_office, visit_workplace, visit_shop, visit_home, visit_john_lewis


# Tool definitions for each game action
TOOLS = [
    {
        "name": "apply_for_job",
        "description": "Apply for a job at the job office based on the player's current qualifications. Better qualifications lead to better paying jobs.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "study",
        "description": "Study at the university to improve qualifications. Costs money but unlocks better job opportunities. Progresses from: None -> High School -> Bachelor -> Master -> PhD",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "work",
        "description": "Go to work and earn money based on the player's current job and wage. Requires having a job first.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "buy_item",
        "description": "Buy an item from the food shop. Multiple items are available",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rest",
        "description": "Rest at home to reduce tiredness and recover energy. A good way to recharge after a busy day.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "buy_john_lewis_item",
        "description": "Buy clothes or furniture from John Lewis department store. Items are stored in inventory. Available: clothing (coats, suits, dresses, shoes) and furniture (chairs, tables, lamps).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def execute_tool(tool_name: str, arguments: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool and return the result

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments (currently unused but kept for future expansion)
        game_state: Current game state

    Returns:
        Dict containing:
            - success: bool
            - message: str
            - updated_state: dict (if success)
    """
    tool_handlers = {
        'apply_for_job': visit_job_office,
        'study': visit_university,
        'work': visit_workplace,
        'buy_item': visit_shop,
        'rest': visit_home,
        'buy_john_lewis_item': visit_john_lewis
    }

    handler = tool_handlers.get(tool_name)
    if not handler:
        return {
            'success': False,
            'message': f'Unknown tool: {tool_name}',
            'updated_state': game_state
        }

    # Execute the action
    updated_state, message, success = handler(game_state)

    return {
        'success': success,
        'message': message,
        'updated_state': updated_state
    }


def get_tools_for_context(context: str) -> list:
    """
    Get available tools based on the current context/location

    Args:
        context: The current location (university, job_office, workplace, shop)

    Returns:
        List of tool definitions available in this context
    """
    context_tools = {
        'university': ['study'],
        'job_office': ['apply_for_job'],
        'workplace': ['work'],
        'shop': ['buy_item'],
        'home': ['rest'],
        'john_lewis': ['buy_john_lewis_item']
    }

    available_tool_names = context_tools.get(context, [])
    return [tool for tool in TOOLS if tool['name'] in available_tool_names]
