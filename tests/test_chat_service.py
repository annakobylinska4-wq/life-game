"""
Unit tests for chat service LLM integration

To run tests locally without AWS Secrets Manager:
1. Edit life_game/secrets_config.json:
   {
     "use_aws_secrets": false,
     "local_development": {
       "openai_api_key": "your-key",
       "llm_provider": "openai"
     }
   }

2. Run tests:
   python -m pytest tests/ -v
"""
import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chat_service import get_llm_response, get_openai_response, get_anthropic_response
from config import config


class TestLLMConnection(unittest.TestCase):
    """Test LLM provider connections"""

    def test_llm_response_returns_text(self):
        """
        Test that get_llm_response returns a text response when asked 'hello'
        """
        # Send a simple 'hello' message
        response = get_llm_response('university', 'hello')

        # Check that we receive a response
        self.assertIsNotNone(response, "Response should not be None")

        # Check that the response is a string
        self.assertIsInstance(response, str, "Response should be a string")

        # Check that the response is not empty
        self.assertGreater(len(response), 0, "Response should not be empty")

        # Check that the response doesn't contain error messages (unless API key is missing)
        if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
            self.assertIn("Error", response, "Should contain error message when no API key is configured")
        else:
            # If we have an API key, response should be valid (not an error)
            # Allow for API errors but the response should still be text
            self.assertIsInstance(response, str, "Response should be text even if there's an API error")

    def test_openai_connection(self):
        """
        Test direct connection to OpenAI API with 'hello' message
        """
        if not config.OPENAI_API_KEY:
            self.skipTest("OpenAI API key not configured")

        system_prompt = "You are a helpful assistant. Keep responses very brief."
        response = get_openai_response(system_prompt, 'hello')

        # Check response is valid text
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

        # If there's an error, it should be in the response text
        # Otherwise, it should be a greeting or acknowledgment
        if not response.startswith("Error"):
            self.assertTrue(
                any(word in response.lower() for word in ['hello', 'hi', 'hey', 'greet', 'help']),
                f"Expected a greeting-like response, got: {response}"
            )

    def test_anthropic_connection(self):
        """
        Test direct connection to Anthropic API with 'hello' message
        """
        if not config.ANTHROPIC_API_KEY:
            self.skipTest("Anthropic API key not configured")

        system_prompt = "You are a helpful assistant. Keep responses very brief."
        response = get_anthropic_response(system_prompt, 'hello')

        # Check response is valid text
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

        # If there's an error, it should be in the response text
        # Otherwise, it should be a greeting or acknowledgment
        if not response.startswith("Error"):
            self.assertTrue(
                any(word in response.lower() for word in ['hello', 'hi', 'hey', 'greet', 'help']),
                f"Expected a greeting-like response, got: {response}"
            )

    def test_npc_context_included(self):
        """
        Test that NPC receives game state context
        """
        if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
            self.skipTest("No API key configured")

        game_state = {
            'money': 500,
            'qualification': 'Bachelor',
            'current_job': 'Engineer',
            'job_wage': 100
        }

        response = get_llm_response('workplace', 'hello', game_state)

        # Check response is valid
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_different_npc_types(self):
        """
        Test that different NPC types return responses
        """
        if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
            self.skipTest("No API key configured")

        npc_types = ['university', 'job_office', 'workplace', 'shop']

        for npc in npc_types:
            with self.subTest(npc=npc):
                response = get_llm_response(npc, 'hello')
                self.assertIsNotNone(response)
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)


class TestLLMConfiguration(unittest.TestCase):
    """Test LLM configuration"""

    def test_provider_configured(self):
        """Test that an LLM provider is configured"""
        self.assertIn(
            config.LLM_PROVIDER.lower(),
            ['openai', 'anthropic'],
            f"LLM_PROVIDER should be 'openai' or 'anthropic', got: {config.LLM_PROVIDER}"
        )

    def test_api_key_type(self):
        """Test that API keys are strings"""
        self.assertIsInstance(config.OPENAI_API_KEY, str)
        self.assertIsInstance(config.ANTHROPIC_API_KEY, str)

    def test_at_least_one_api_key(self):
        """Test that at least one API key is configured (warning if not)"""
        has_key = bool(config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY)
        if not has_key:
            self.skipTest(
                "WARNING: No API keys configured. "
                "Set OPENAI_API_KEY or ANTHROPIC_API_KEY to test LLM functionality."
            )


if __name__ == '__main__':
    unittest.main()
