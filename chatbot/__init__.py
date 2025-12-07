"""
Chatbot library for handling NPC conversations and LLM interactions
"""
from .llm_client import get_llm_response
from .prompts import load_npc_prompts

__all__ = ['get_llm_response', 'load_npc_prompts']
