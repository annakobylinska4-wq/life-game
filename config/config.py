"""
Configuration file for the Life Game application
"""
import secrets
import os
import json
from loguru import logger



def _load_json_file(path):
    """Load a JSON file, raising if not found"""
    with open(path, 'r') as f:
        return json.load(f)


def _load_llm_secrets(use_aws_secrets, aws_config, local_secrets):
    """Load LLM secrets from AWS or local config"""
    if use_aws_secrets:
        logger.info("Loading LLM secrets from AWS Secrets Manager")
        try:
            # Try absolute import first (works in Docker container)
            from utils.aws_secrets import get_llm_secrets
            return get_llm_secrets(
                aws_config['aws_secret_name'],
                aws_config['aws_region']
            )
        except ImportError:
            # Try relative import as fallback (for running as package)
            try:
                from ..utils.aws_secrets import get_llm_secrets
                return get_llm_secrets(
                    aws_config['aws_secret_name'],
                    aws_config['aws_region']
                )
            except Exception as e:
                logger.Warning(f"Warning: Could not load from AWS: {e}, using local config")
        except Exception as e:
            logger.Warning(f"Warning: Could not load from AWS: {e}, using local config")

    logger.info("Loading LLM secrets from local config")
    return {
        'openai_api_key': local_secrets.get('openai_api_key', ''),
        'anthropic_api_key': local_secrets.get('anthropic_api_key', ''),
        'llm_provider': local_secrets.get('llm_provider', 'openai')
    }

def _load_sessionmng_secrets(use_aws_secrets,aws_config, local_secrets):
    """Load session management secrets from AWS or local config"""
    if use_aws_secrets:
        logger.info("Loading session management secrets from AWS Secrets Manager")
        try:
            # Try absolute import first (works in Docker container)
            from utils.aws_secrets import get_sessionmng_secrets
            return get_sessionmng_secrets(
                aws_config['aws_session_mng'],
                aws_config['aws_region']
            )
        except ImportError:
            # Try relative import as fallback (for running as package)
            try:
                from ..utils.aws_secrets import get_llm_secrets
                return get_sessionmng_secrets(
                    aws_config['aws_session_mng'],
                    aws_config['aws_region']
                )
            except Exception as e:
                logger.Warning("Warning: Could not load from AWS: {e}, using local config")
        except Exception as e:
            logger.Warning("Warning: Could not load from AWS: {e}, using local config")
    
    logger.info("Loading session management secrets from local config")
    return {
        'sessionmng_key': local_secrets.get('session_mng', '')
    }




class Config:
    """Application configuration"""

    # flag indicating local or AWS S3 storage
    USE_AWS_STORAGE = False
    USE_AWS_SECRETS = True

    # Load configs at module import time
    _config_dir = os.path.dirname(__file__)
    _aws_config = _load_json_file(os.path.join(_config_dir, 'aws_secrets_config.json'))
    _local_secrets = _load_json_file(os.path.join(_config_dir, 'secrets_config.json'))
    _llm_config = _load_json_file(os.path.join(_config_dir, 'llm_config.json'))
    _llm_secrets = _load_llm_secrets(USE_AWS_SECRETS,_aws_config, _local_secrets)
    _sessionmng_secrets = _load_sessionmng_secrets(USE_AWS_SECRETS,_aws_config, _local_secrets)

    # secret key for session management
    SECRET_KEY = _sessionmng_secrets.get('sessionmng_key', '')

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

# Default configuration to use
config = Config()
