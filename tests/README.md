# Test Suite for Life Game

## Overview

This directory contains unit tests for the Life Game, specifically testing the LLM chat service integration.

## Setup

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have configured at least one LLM API key (see [CHAT_SETUP.md](../../CHAT_SETUP.md)):
```bash
export OPENAI_API_KEY='your-key'
# OR
export ANTHROPIC_API_KEY='your-key'
```

## Running Tests

### Run all tests:
```bash
# From the life_game directory
python -m pytest tests/

# Or with verbose output
python -m pytest tests/ -v

# Or run the test file directly
python -m unittest tests/test_chat_service.py
```

### Run specific test:
```bash
# Run a specific test class
python -m pytest tests/test_chat_service.py::TestLLMConnection

# Run a specific test method
python -m pytest tests/test_chat_service.py::TestLLMConnection::test_llm_response_returns_text
```

## Test Coverage

### `test_chat_service.py`

#### TestLLMConnection
- **`test_llm_response_returns_text()`**: Tests that sending 'hello' to the LLM returns a text response
- **`test_openai_connection()`**: Tests direct OpenAI API connection (skipped if no API key)
- **`test_anthropic_connection()`**: Tests direct Anthropic API connection (skipped if no API key)
- **`test_npc_context_included()`**: Tests that game state is passed to the LLM
- **`test_different_npc_types()`**: Tests all NPC types (professor, clerk, boss, shopkeeper)

#### TestLLMConfiguration
- **`test_provider_configured()`**: Verifies LLM provider is set to valid value
- **`test_api_key_type()`**: Verifies API keys are strings
- **`test_at_least_one_api_key()`**: Warns if no API keys are configured

## Expected Output

With API keys configured:
```
test_anthropic_connection (__main__.TestLLMConnection) ... ok
test_different_npc_types (__main__.TestLLMConnection) ... ok
test_llm_response_returns_text (__main__.TestLLMConnection) ... ok
test_npc_context_included (__main__.TestLLMConnection) ... ok
test_openai_connection (__main__.TestLLMConnection) ... ok
test_api_key_type (__main__.TestLLMConfiguration) ... ok
test_at_least_one_api_key (__main__.TestLLMConfiguration) ... ok
test_provider_configured (__main__.TestLLMConfiguration) ... ok

----------------------------------------------------------------------
Ran 8 tests in X.XXs

OK
```

Without API keys configured:
- Tests requiring API keys will be skipped
- You'll see warnings about missing API keys
- Configuration tests will still run

## Notes

- Tests make actual API calls to OpenAI/Anthropic, which may incur small costs
- Tests will be skipped if the required API key is not configured
- The 'hello' test is intentionally simple to verify basic connectivity
- Tests verify that responses are non-empty strings
- OpenAI/Anthropic tests check for greeting-like responses

## Troubleshooting

**Tests are being skipped:**
- Check that your API key environment variable is set
- Make sure you've set the correct `LLM_PROVIDER` in config.py or environment

**Tests fail with API errors:**
- Verify your API key is valid and has credits
- Check your internet connection
- Check the provider's status page for outages

**Import errors:**
- Make sure you're running tests from the `life_game` directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`
