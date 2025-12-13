"""
Module for loading and managing NPC system prompts
"""
import os

import yaml


def load_npc_prompts():
    """
    Load NPC system prompts from YAML file

    Returns:
        dict: Dictionary mapping NPC types to their system prompts
    """
    prompts_file = os.path.join(os.path.dirname(__file__), 'npc_prompts.yaml')

    try:
        with open(prompts_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: NPC prompts file not found at {prompts_file}")
        return {}
    except yaml.YAMLError as e:
        print(f"Warning: Error parsing NPC prompts YAML: {e}")
        return {}


def get_npc_prompt(npc_type, game_state=None):
    """
    Get system prompt for a specific NPC type with optional game state context

    Args:
        npc_type: The type of NPC (university, job_office, workplace, shop)
        game_state: Optional game state to add to the prompt

    Returns:
        str: The complete system prompt
    """
    prompts = load_npc_prompts()
    system_prompt = prompts.get(npc_type, "You are a helpful assistant.")

    # Add game state context if provided
    if game_state:
        context = f"\n\nCurrent player status:\n"
        context += f"- Money: ${game_state.get('money', 0)}\n"
        context += f"- Qualification: {game_state.get('qualification', 'None')}\n"
        context += f"- Current Job: {game_state.get('current_job', 'Unemployed')}\n"
        context += f"- Wage: ${game_state.get('job_wage', 0)}/turn\n"
        system_prompt += context

    return system_prompt
