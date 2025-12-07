"""
Chat service for handling LLM-based conversations with NPCs
Now supports MCP tool calling for triggering game actions
"""
from config import config
from mcp_server.tools import get_tools_for_context, execute_tool


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
and unlock better jobs. Be encouraging and helpful!

When the student wants to study or enroll in a course, use the 'study' tool to help them.""",

    'job_office': """You are a professional and helpful job office clerk.
You assist people in finding employment opportunities that match their qualifications.
You should:
- Be professional and efficient
- Discuss job opportunities and career paths
- Explain how qualifications affect job availability
- Keep responses concise (2-3 sentences)
- Stay in character as a job office clerk

The person is playing a life simulation game where they can find jobs based on their education level.
Help them understand the job market and opportunities available!

When someone wants to apply for a job or find work, use the 'apply_for_job' tool to help them.""",

    'workplace': """You are the player's boss at their workplace.
You manage the team and oversee the player's work performance.
You should:
- Be professional but approachable
- Discuss work, productivity, and career growth
- Acknowledge the player's efforts and contributions
- Keep responses concise (2-3 sentences)
- Stay in character as a workplace supervisor

The employee is playing a life simulation game where they work to earn money.
Be a realistic boss - professional, fair, and occasionally motivating!

When the employee wants to work or complete their shift, use the 'work' tool.""",

    'shop': """You are a friendly and persuasive shopkeeper.
You run a store that sells various items to help people show off their success.
You should:
- Be friendly and enthusiastic about your products
- Discuss items available for purchase
- Be a bit salesy but not pushy
- Keep responses concise (2-3 sentences)
- Stay in character as a shopkeeper

The customer is playing a life simulation game where they can buy items with their earned money.
Be welcoming and help them find what they're looking for!

When a customer wants to buy something, use the 'buy_item' tool to process the purchase."""
}


def get_llm_response(action, user_message, game_state=None):
    """
    Get a response from the LLM based on the action and user message
    Now supports MCP tool calling

    Args:
        action: The location/action (university, job_office, workplace, shop)
        user_message: The user's chat message
        game_state: Optional game state to provide context

    Returns:
        dict: Contains 'response' (str), 'tool_calls' (list), 'updated_state' (dict or None)
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
        return get_openai_response_with_tools(system_prompt, user_message, action, game_state)
    elif provider == 'anthropic':
        return get_anthropic_response_with_tools(system_prompt, user_message, action, game_state)
    else:
        return {
            'response': "Error: Invalid LLM provider configuration.",
            'tool_calls': [],
            'updated_state': None
        }


def get_openai_response_with_tools(system_prompt, user_message, context, game_state):
    """Get response from OpenAI API with MCP tool support"""
    try:
        from openai import OpenAI

        if not config.OPENAI_API_KEY:
            return {
                'response': "Error: OpenAI API key not configured. Please configure secrets_config.json.",
                'tool_calls': [],
                'updated_state': None
            }

        # Get available tools for this context
        available_tools = get_tools_for_context(context)

        # Convert to OpenAI function format
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            for tool in available_tools
        ]

        # Get model configuration from llm_config.json
        model_config = config.get_llm_model_config('openai')

        client = OpenAI(api_key=config.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=model_config.get('model', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=openai_tools if openai_tools else None,
            max_tokens=model_config.get('max_tokens', 150),
            temperature=model_config.get('temperature', 0.7),
            top_p=model_config.get('top_p', 1.0),
            frequency_penalty=model_config.get('frequency_penalty', 0.0),
            presence_penalty=model_config.get('presence_penalty', 0.0)
        )

        message = response.choices[0].message
        tool_results = []
        updated_state = game_state

        # Handle tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = {}
                if tool_call.function.arguments:
                    import json
                    tool_args = json.loads(tool_call.function.arguments)

                # Execute the tool
                result = execute_tool(tool_name, tool_args, updated_state)
                tool_results.append(result)

                if result['success']:
                    updated_state = result['updated_state']

            # Get final response incorporating tool results
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": message.content, "tool_calls": message.tool_calls},
            ]

            for tool_call, result in zip(message.tool_calls, tool_results):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result['message']
                })

            final_response = client.chat.completions.create(
                model=model_config.get('model', 'gpt-4o-mini'),
                messages=messages,
                max_tokens=model_config.get('max_tokens', 150),
                temperature=model_config.get('temperature', 0.7)
            )

            return {
                'response': final_response.choices[0].message.content.strip(),
                'tool_calls': tool_results,
                'updated_state': updated_state
            }

        return {
            'response': message.content.strip() if message.content else "",
            'tool_calls': [],
            'updated_state': None
        }

    except ImportError:
        return {
            'response': "Error: OpenAI library not installed. Run: pip install openai",
            'tool_calls': [],
            'updated_state': None
        }
    except Exception as e:
        return {
            'response': f"Error communicating with OpenAI: {str(e)}",
            'tool_calls': [],
            'updated_state': None
        }


def get_anthropic_response_with_tools(system_prompt, user_message, context, game_state):
    """Get response from Anthropic API with MCP tool support"""
    try:
        import anthropic

        if not config.ANTHROPIC_API_KEY:
            return {
                'response': "Error: Anthropic API key not configured. Please configure secrets_config.json.",
                'tool_calls': [],
                'updated_state': None
            }

        # Get available tools for this context
        available_tools = get_tools_for_context(context)

        # Convert to Anthropic tool format
        anthropic_tools = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["inputSchema"]
            }
            for tool in available_tools
        ]

        # Get model configuration from llm_config.json
        model_config = config.get_llm_model_config('anthropic')

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model=model_config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=model_config.get('max_tokens', 1024),
            temperature=model_config.get('temperature', 0.7),
            top_p=model_config.get('top_p', 1.0),
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            tools=anthropic_tools if anthropic_tools else None
        )

        tool_results = []
        updated_state = game_state

        # Handle tool calls
        if response.stop_reason == "tool_use":
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_args = content_block.input

                    # Execute the tool
                    result = execute_tool(tool_name, tool_args, updated_state)
                    tool_results.append(result)

                    if result['success']:
                        updated_state = result['updated_state']

            # Get final response incorporating tool results
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response.content}
            ]

            tool_result_content = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    # Find corresponding result
                    for result in tool_results:
                        tool_result_content.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": result['message']
                        })
                        break

            messages.append({
                "role": "user",
                "content": tool_result_content
            })

            final_response = client.messages.create(
                model=model_config.get('model', 'claude-3-5-sonnet-20241022'),
                max_tokens=model_config.get('max_tokens', 1024),
                temperature=model_config.get('temperature', 0.7),
                system=system_prompt,
                messages=messages
            )

            return {
                'response': final_response.content[0].text.strip(),
                'tool_calls': tool_results,
                'updated_state': updated_state
            }

        # No tool calls, just return the text response
        text_content = ""
        for content_block in response.content:
            if hasattr(content_block, 'text'):
                text_content += content_block.text

        return {
            'response': text_content.strip(),
            'tool_calls': [],
            'updated_state': None
        }

    except ImportError:
        return {
            'response': "Error: Anthropic library not installed. Run: pip install anthropic",
            'tool_calls': [],
            'updated_state': None
        }
    except Exception as e:
        return {
            'response': f"Error communicating with Anthropic: {str(e)}",
            'tool_calls': [],
            'updated_state': None
        }
