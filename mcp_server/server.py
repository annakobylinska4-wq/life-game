"""
Tool Server for Life Game
This file is kept for future MCP implementation but is not currently used.
The app uses native OpenAI/Anthropic function calling instead.

To implement true MCP in the future, you would:
1. Install: pip install mcp
2. Implement MCP protocol server here
3. Connect Claude Desktop or other MCP clients to this server
"""
from typing import Any, Dict, Optional
from .tools import TOOLS, execute_tool, get_tools_for_context


# Placeholder for future MCP server implementation
# Currently the app uses direct function calling in chat_service.py
