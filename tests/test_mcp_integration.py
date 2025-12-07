"""
Test script for MCP integration
Demonstrates how the chat service triggers game actions
"""
from chat_service import get_llm_response


def test_job_office_chat():
    """Test applying for a job via chat"""
    print("=" * 60)
    print("TEST: Job Office Chat with MCP Tool Calling")
    print("=" * 60)

    # Initial game state
    game_state = {
        'money': 100,
        'items': [],
        'qualification': 'Bachelor',
        'current_job': 'Unemployed',
        'job_wage': 0,
        'turn': 1
    }

    print("\nInitial State:")
    print(f"  Qualification: {game_state['qualification']}")
    print(f"  Job: {game_state['current_job']}")
    print(f"  Money: ${game_state['money']}")

    # User chats with job office clerk
    user_message = "Hi! I'd like to apply for a job please."

    print(f"\nUser: {user_message}")

    # Get LLM response (should trigger apply_for_job tool)
    result = get_llm_response('job_office', user_message, game_state)

    print(f"\nNPC Response: {result['response']}")

    if result['tool_calls']:
        print("\nTools Called:")
        for tool_call in result['tool_calls']:
            print(f"  - {tool_call.get('message', 'Unknown tool')}")

        print("\nUpdated State:")
        updated_state = result['updated_state']
        print(f"  Qualification: {updated_state['qualification']}")
        print(f"  Job: {updated_state['current_job']}")
        print(f"  Wage: ${updated_state['job_wage']}/turn")
        print(f"  Money: ${updated_state['money']}")
    else:
        print("\nNo tools were called (LLM just chatted)")

    print("\n" + "=" * 60)


def test_university_chat():
    """Test studying via chat"""
    print("\nTEST: University Chat with MCP Tool Calling")
    print("=" * 60)

    # Initial game state
    game_state = {
        'money': 500,
        'items': [],
        'qualification': 'High School',
        'current_job': 'Cashier',
        'job_wage': 35,
        'turn': 5
    }

    print("\nInitial State:")
    print(f"  Qualification: {game_state['qualification']}")
    print(f"  Money: ${game_state['money']}")

    # User chats with professor
    user_message = "I want to improve my education. Can I enroll in a degree program?"

    print(f"\nUser: {user_message}")

    # Get LLM response (should trigger study tool)
    result = get_llm_response('university', user_message, game_state)

    print(f"\nProfessor Response: {result['response']}")

    if result['tool_calls']:
        print("\nTools Called:")
        for tool_call in result['tool_calls']:
            print(f"  - {tool_call.get('message', 'Unknown tool')}")

        print("\nUpdated State:")
        updated_state = result['updated_state']
        print(f"  Qualification: {updated_state['qualification']}")
        print(f"  Money: ${updated_state['money']}")
    else:
        print("\nNo tools were called (LLM just chatted)")

    print("\n" + "=" * 60)


def test_casual_chat():
    """Test casual conversation that shouldn't trigger tools"""
    print("\nTEST: Casual Chat (No Tool Calling Expected)")
    print("=" * 60)

    game_state = {
        'money': 200,
        'items': [],
        'qualification': 'Bachelor',
        'current_job': 'Office Worker',
        'job_wage': 60,
        'turn': 10
    }

    print("\nInitial State:")
    print(f"  Job: {game_state['current_job']}")

    # User just chats without requesting action
    user_message = "How's the weather today?"

    print(f"\nUser: {user_message}")

    result = get_llm_response('workplace', user_message, game_state)

    print(f"\nBoss Response: {result['response']}")

    if result['tool_calls']:
        print("\nUnexpected: Tools were called!")
    else:
        print("\nCorrect: No tools were called (casual conversation)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n🎮 MCP Integration Test Suite\n")
    print("This demonstrates how LLM conversations can trigger game actions")
    print("using MCP tools based on user intent.\n")

    try:
        test_job_office_chat()
        test_university_chat()
        test_casual_chat()

        print("\n✅ All tests completed!")
        print("\nNote: You need to have LLM_PROVIDER and API keys configured")
        print("in your config for this to work with real LLM responses.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\nMake sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Configured your API keys in secrets_config.json")
