"""
Chat service for handling LLM-based conversations with NPCs
Now uses the chatbot library for modular LLM interactions
"""
from chatbot import get_llm_response

# Re-export for backward compatibility
__all__ = ['get_llm_response']
