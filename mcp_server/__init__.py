"""
Tool definitions for Life Game
Exposes game actions as tools for LLM function calling
"""
from .tools import TOOLS, execute_tool, get_tools_for_context

__all__ = ['TOOLS', 'execute_tool', 'get_tools_for_context']
