"""
Configuration file for the Life Game application
"""
import secrets
import os
import json


def _load_json_file(path):
    """Load a JSON file, raising if not found"""
    with open(path, 'r') as f:
        return json.load(f)


def _load_llm_secrets(aws_config, local_secrets):
    """Load LLM secrets from AWS or local config"""
    if aws_config.get('use_aws_secrets'):
        try:
            from ..utils.aws_secrets import get_llm_secrets
            return get_llm_secrets(
                aws_config['aws_secret_name'],
                aws_config['aws_region']
            )
        except Exception as e:
            print(f"Warning: Could not load from AWS: {e}, using local config")

    return {
        'openai_api_key': local_secrets.get('openai_api_key', ''),
        'anthropic_api_key': local_secrets.get('anthropic_api_key', ''),
        'llm_provider': local_secrets.get('llm_provider', 'openai')
    }


# Load configs at module import time
_config_dir = os.path.dirname(__file__)
_aws_config = _load_json_file(os.path.join(_config_dir, 'aws_secrets_config.json'))
_local_secrets = _load_json_file(os.path.join(_config_dir, 'secrets_config.json'))
_llm_config = _load_json_file(os.path.join(_config_dir, 'llm_config.json'))
_llm_secrets = _load_llm_secrets(_aws_config, _local_secrets)


class Config:
    """Application configuration"""

    # secret key for session management
    SECRET_KEY = '94d879fbfd41c394d07041cb9b7ce606a5825b9634838d5d11a918976c2e6bc1'

    # Server configuration
    PORT = 5001
    DEBUG = True

    # Data storage configuration
    DATA_DIR = 'data'
    USERS_FILE = 'users.json'
    GAME_STATES_FILE = 'game_states.json'

    # Game configuration
    INITIAL_MONEY = 100
    UNIVERSITY_COST = 50
    INITIAL_HAPPINESS = 50
    INITIAL_TIREDNESS = 0
    INITIAL_HUNGER = 0

    # AWS Secrets Manager configuration
    AWS_REGION = _aws_config.get('aws_region')
    AWS_SECRET_NAME = _aws_config.get('aws_secret_name')

    # LLM API keys
    OPENAI_API_KEY = _llm_secrets.get('openai_api_key', '')
    ANTHROPIC_API_KEY = _llm_secrets.get('anthropic_api_key', '')
    LLM_PROVIDER = _llm_secrets.get('llm_provider', 'openai')

    @staticmethod
    def get_llm_model_config(provider=None):
        """Get LLM model configuration for a specific provider"""
        if provider is None:
            provider = _llm_secrets.get('llm_provider', 'openai')
        return _llm_config.get(provider, _llm_config.get('openai', {}))

    @staticmethod
    def generate_secret_key():
        """Generate a secure random secret key"""
        return secrets.token_hex(32)

# You can create different config classes for different environments
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    # In production, you should set SECRET_KEY from environment variable
    # SECRET_KEY = os.environ.get('SECRET_KEY') or Config.generate_secret_key()


# Default configuration to use
config = Config()
