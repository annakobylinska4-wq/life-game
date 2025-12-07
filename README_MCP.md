# MCP Integration Guide

## Overview

Your Life Game now supports **MCP (Model Context Protocol)** integration, allowing the LLM to intelligently trigger game actions based on natural conversation.

## What Changed?

### Before (Manual Actions)
- User clicks "Visit Job Office" button → Gets a job
- Chat was separate, only for conversation

### After (MCP Tool Calling)
- User chats: "I'd like to apply for a job" → **LLM automatically triggers the job application**
- User chats: "I want to study" → **LLM automatically enrolls them in university**
- Actions happen naturally through conversation!

## Architecture

```
┌─────────────┐
│   User      │
│   Chat      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  chat_service   │  ← Sends message + available tools to LLM
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   LLM (OpenAI/  │  ← Decides if action needed
│   Anthropic)    │  ← Returns response + tool calls
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  mcp_server/    │  ← Executes game actions
│  tools.py       │  ← Returns results
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Updated State  │  ← Saved to database
└─────────────────┘
```

## Available Tools (by Location)

### Job Office
- **Tool**: `apply_for_job`
- **Triggers when**: User wants to find/apply for a job
- **Examples**:
  - "I'd like to apply for a job"
  - "Can you help me find work?"
  - "I need employment"

### University
- **Tool**: `study`
- **Triggers when**: User wants to study/improve education
- **Examples**:
  - "I want to study"
  - "Can I enroll in a degree program?"
  - "I'd like to improve my qualifications"

### Workplace
- **Tool**: `work`
- **Triggers when**: User wants to work/earn money
- **Examples**:
  - "I'm ready to work"
  - "Let me do my shift"
  - "Time to earn some money"

### Shop
- **Tool**: `buy_item`
- **Triggers when**: User wants to purchase something
- **Examples**:
  - "I'd like to buy something"
  - "What can I purchase?"
  - "I want to shop"

## Key Files

### `/mcp_server/tools.py`
- Defines all available MCP tools
- Maps tools to game actions
- Handles tool execution

### `/mcp_server/server.py`
- MCP server implementation (for future standalone use)
- Can be run independently if needed

### `/chat_service.py`
- Refactored to use MCP tool calling
- Supports both OpenAI and Anthropic
- Handles tool execution flow

### `/app.py`
- Updated `/api/chat` endpoint
- Automatically saves state when tools are called
- Returns tool results to frontend

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure you have API keys configured in secrets_config.json
```

## Testing

Run the test script to see MCP in action:

```bash
cd life_game
python test_mcp_integration.py
```

This will demonstrate:
1. ✅ Job application via chat
2. ✅ Studying via chat
3. ✅ Casual conversation (no tool calling)

## Response Format

The `/api/chat` endpoint now returns:

```json
{
  "success": true,
  "response": "Great! I've signed you up for an Office Worker position...",
  "tool_calls": [
    {
      "success": true,
      "message": "You secured a job as Office Worker earning $60 per turn!",
      "updated_state": { /* new game state */ }
    }
  ],
  "state": { /* updated game state */ }
}
```

## Future Extensibility

The MCP architecture makes it easy to add new actions:

1. **Add new action** to `/actions/` directory
2. **Define tool** in `/mcp_server/tools.py`
3. **Update system prompt** in `/chat_service.py`
4. Done! LLM can now trigger the action

### Example: Adding a "Bank" location

```python
# In mcp_server/tools.py
TOOLS.append({
    "name": "deposit_money",
    "description": "Deposit money into savings account to earn interest",
    "inputSchema": {
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "Amount to deposit"}
        },
        "required": ["amount"]
    }
})
```

## Benefits of MCP

1. **Natural Interaction**: Users chat naturally instead of clicking buttons
2. **Intent Recognition**: LLM understands various phrasings
3. **Extensible**: Easy to add new actions and tools
4. **Future-proof**: Can connect to other MCP-compatible systems
5. **Flexible**: Works with multiple LLM providers (OpenAI, Anthropic)

## Notes

- Tools are **context-specific**: Only relevant tools are available at each location
- LLM is **smart**: It won't trigger actions for casual conversation
- State updates are **automatic**: Game state saved when tools execute
- **Backward compatible**: Old button-based actions still work via `/api/action` endpoint
