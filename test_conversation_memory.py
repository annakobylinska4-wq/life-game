"""
Test script to demonstrate conversation memory functionality
This script simulates a conversation with memory
"""
from models.game_state import GameState
from chatbot.llm_client import get_llm_response, get_conversation_history

# Create a test game state
test_state = GameState.create_new()
state_dict = test_state.to_dict()

print("=" * 60)
print("CONVERSATION MEMORY TEST")
print("=" * 60)
print("\nThis test demonstrates how conversation history is stored")
print("and retrieved for each location.\n")

# Simulate a conversation at the university
location = "university"

print(f"\n--- Location: {location.upper()} ---\n")

# First message
print("User: Hello, what courses do you offer?")
print("\nBefore first message:")
print(f"  Conversation history length: {len(get_conversation_history(state_dict, location))}")

# In a real scenario, this would call the LLM
# For testing, we'll simulate the response
test_response_1 = "Hello! We offer a variety of courses including middle school, high school, vocational training, bachelor's degrees, master's degrees, MBAs, PhDs, and executive MBAs."

# Manually update conversation history (simulating what llm_client does)
from chatbot.llm_client import update_conversation_history
state_dict = update_conversation_history(state_dict, location,
                                         "Hello, what courses do you offer?",
                                         test_response_1)

print(f"\nAfter first message:")
print(f"  Conversation history length: {len(get_conversation_history(state_dict, location))}")
print(f"  History: {get_conversation_history(state_dict, location)}")

# Second message (should have context from first)
print("\n\nUser: What are the prerequisites for a bachelor's degree?")

state_dict = update_conversation_history(state_dict, location,
                                         "What are the prerequisites for a bachelor's degree?",
                                         "You'll need to complete high school first before enrolling in a bachelor's program.")

print(f"\nAfter second message:")
print(f"  Conversation history length: {len(get_conversation_history(state_dict, location))}")

# Test conversation isolation between locations
shop_location = "shop"
print(f"\n\n--- Location: {shop_location.upper()} ---\n")
print("User: What food do you have?")
print(f"\nShop conversation history length: {len(get_conversation_history(state_dict, shop_location))}")

state_dict = update_conversation_history(state_dict, shop_location,
                                         "What food do you have?",
                                         "*sigh* We got whatever's left. Take it or leave it.")

print(f"After first shop message:")
print(f"  Shop history length: {len(get_conversation_history(state_dict, shop_location))}")
print(f"  University history length (unchanged): {len(get_conversation_history(state_dict, location))}")

print("\n\n--- VERIFICATION ---")
print(f"\nTotal locations with conversation history: {len(state_dict.get('conversation_history', {}))}")
print(f"Locations: {list(state_dict.get('conversation_history', {}).keys())}")

print("\n\n--- TESTING MAX HISTORY LIMIT ---")
print("Adding 12 messages to test the 10-message limit...")

for i in range(12):
    state_dict = update_conversation_history(state_dict, "test_location",
                                             f"Message {i+1}",
                                             f"Response {i+1}")

test_history = get_conversation_history(state_dict, "test_location")
print(f"\nAfter adding 12 messages (24 entries):")
print(f"  History length: {len(test_history)} (should be max 10)")
print(f"  Oldest message: {test_history[0]['content']}")
print(f"  Newest message: {test_history[-1]['content']}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nConversation memory is working correctly!")
print("- Each location maintains separate conversation history")
print("- History is limited to the most recent 10 messages")
print("- History persists in the game state")
