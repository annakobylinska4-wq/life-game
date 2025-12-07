"""
Chat service for handling LLM-based conversations with NPCs
"""
from config import config


# System prompts for each NPC type
NPC_SYSTEM_PROMPTS = {
    'university': """You are a knowledgeable and encouraging university professor.
You help students understand the value of education and guide them in their academic journey.
You should:
- Be supportive and motivating
- Discuss education, learning, and career prospects
- Explain how different qualifications can lead to better job opportunities
- Keep responses concise (2-3 sentences)
- Stay in character as a professor at a university

The student is playing a life simulation game where they can study to improve their qualifications
and unlock better jobs. Be encouraging and helpful!""",

    'job_office': """You are a professional and helpful job office clerk.
You assist people in finding employment opportunities that match their qualifications.
You should:
- Be professional and efficient
- Discuss job opportunities and career paths
- Explain how qualifications affect job availability
- Keep responses concise (2-3 sentences)
- Stay in character as a job office clerk

The person is playing a life simulation game where they can find jobs based on their education level.
Help them understand the job market and opportunities available!""",

    'workplace': """You are the player's boss at their workplace.
You manage the team and oversee the player's work performance.
You should:
- Be professional but approachable
- Discuss work, productivity, and career growth
- Acknowledge the player's efforts and contributions
- Keep responses concise (2-3 sentences)
- Stay in character as a workplace supervisor

The employee is playing a life simulation game where they work to earn money.
Be a realistic boss - professional, fair, and occasionally motivating!""",

    'shop': """You are a friendly and persuasive shopkeeper.
You run a store that sells various items to help people show off their success.
You should:
- Be friendly and enthusiastic about your products
- Discuss items available for purchase
- Be a bit salesy but not pushy
- Keep responses concise (2-3 sentences)
- Stay in character as a shopkeeper

The customer is playing a life simulation game where they can buy items with their earned money.
Be welcoming and help them find what they're looking for!"""
}


def get_llm_response(action, user_message, game_state=None):
    """
    Get a response from the LLM based on the action and user message

    Args:
        action: The location/action (university, job_office, workplace, shop)
        user_message: The user's chat message
        game_state: Optional game state to provide context

    Returns:
        str: The LLM's response
    """
    system_prompt = NPC_SYSTEM_PROMPTS.get(action, "You are a helpful assistant.")

    # Add game state context if provided
    if game_state:
        context = f"\n\nCurrent player status:\n"
        context += f"- Money: ${game_state.get('money', 0)}\n"
        context += f"- Qualification: {game_state.get('qualification', 'None')}\n"
        context += f"- Current Job: {game_state.get('current_job', 'Unemployed')}\n"
        context += f"- Wage: ${game_state.get('job_wage', 0)}/turn\n"
        system_prompt += context

    provider = config.LLM_PROVIDER.lower()

    if provider == 'openai':
        return get_openai_response(system_prompt, user_message)
    elif provider == 'anthropic':
        return get_anthropic_response(system_prompt, user_message)
    else:
        return "Error: Invalid LLM provider configuration."


def get_openai_response(system_prompt, user_message):
    """Get response from OpenAI API"""
    try:
        from openai import OpenAI

        if not config.OPENAI_API_KEY:
            return "Error: OpenAI API key not configured. Please configure secrets_config.json."

        # Get model configuration from llm_config.json
        model_config = config.get_llm_model_config('openai')

        client = OpenAI(api_key=config.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=model_config.get('model', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=model_config.get('max_tokens', 150),
            temperature=model_config.get('temperature', 0.7),
            top_p=model_config.get('top_p', 1.0),
            frequency_penalty=model_config.get('frequency_penalty', 0.0),
            presence_penalty=model_config.get('presence_penalty', 0.0)
        )

        return response.choices[0].message.content.strip()

    except ImportError:
        return "Error: OpenAI library not installed. Run: pip install openai"
    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"


def get_anthropic_response(system_prompt, user_message):
    """Get response from Anthropic API"""
    try:
        import anthropic

        if not config.ANTHROPIC_API_KEY:
            return "Error: Anthropic API key not configured. Please configure secrets_config.json."

        # Get model configuration from llm_config.json
        model_config = config.get_llm_model_config('anthropic')

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model=model_config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=model_config.get('max_tokens', 150),
            temperature=model_config.get('temperature', 0.7),
            top_p=model_config.get('top_p', 1.0),
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return message.content[0].text.strip()

    except ImportError:
        return "Error: Anthropic library not installed. Run: pip install anthropic"
    except Exception as e:
        return f"Error communicating with Anthropic: {str(e)}"
