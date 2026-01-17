"""
Configuration file for the Life Game application
"""
import os
import json
from loguru import logger

from utils.aws_secrets import SecretsManager, get_secrets_manager

def _load_json_file(path):
    """Load a JSON file, raising if not found"""
    with open(path, 'r') as f:
        return json.load(f)

def get_llm_secrets(secret_name, region_name=None):
    """
    Retrieve LLM API keys from AWS Secrets Manager

    Expected secret format (JSON):
    {
        "openai_api_key": "sk-...",
        "anthropic_api_key": "sk-ant-...",
        "llm_provider": "openai"
    } """


    
    logger.info(f"Retrieving LLM secrets from AWS Secrets Manager: {secret_name} in region {region_name}")

    try:
        secrets_manager = get_secrets_manager(region_name)
        secret = secrets_manager.get_secret(secret_name)

        # If secret is a dictionary, return it
        if isinstance(secret, dict):
            logger.info(f"LLM secret retrieved successfully from AWS.")
            return {
                'openai_api_key': secret.get('openai_api_key', ''),
                'anthropic_api_key': secret.get('anthropic_api_key', ''),
                'llm_provider': secret.get('llm_provider', 'openai')
            }

        # If secret is a string, assume it's a single API key
        # Default to openai provider for string secrets
        if isinstance(secret, str):
            logger.info(f"LLM secret retrieved successfully from AWS as string, assuming OpenAI API key.")
            return {
                'openai_api_key': secret,
                'anthropic_api_key': '',
                'llm_provider': 'openai'
            }

    except Exception as e:
        # Log the error but don't crash - return empty keys

        logger.info(f"Warning: Could not retrieve LLM secrets from AWS: {str(e)}")
        return {
            'openai_api_key': '',
            'anthropic_api_key': '',
            'llm_provider': 'openai'
        }

def get_sessionmng_secrets(secret_name='prod/MrJones/SessionMng', region_name=None):
    """
    Retrieve session mng keys from AWS Secrets Manager

    Expected secret format (JSON):
    {
        "session_mng_key": "..."
    }

    Args:
        secret_name: Name of the secret containing LLM API keys
        region_name: AWS region (optional, uses default if not specified)

    Returns:
        str: session management key
    """
    logger.info(f"Retrieving SessionMng secrets from AWS Secrets Manager: {secret_name} in region {region_name}")
    try:
        secrets_manager = get_secrets_manager(region_name)
        secret = secrets_manager.get_secret(secret_name)

        # If secret is a dictionary, return it
        if isinstance(secret, dict):
            logger.info(f"SessionMng secret retrieved successfully from AWS.")
            return {'sessionmng_key': secret.get('session_mng_key', '')
            }

    except Exception as e:

        # Log the error but don't crash - return empty keys
        logger.info(f"Warning: Could not retrieve SessionMng secrets from AWS: {str(e)}")
        return {'sessionmng_key': ''}
        

def _load_secret(use_aws_secrets, aws_config, local_secrets, secret_key):
    """Load secrets either from AWS Secrets Manager or local file"""
    if use_aws_secrets:
        logger.info(f"Loading {secret_key} from AWS Secrets Manager.")
        region_name = aws_config.get('aws_region')
        secret_name = aws_config.get(secret_key)
        if secret_name:
            if secret_key == 'aws_secret_name':
                return get_llm_secrets(secret_name, region_name)
            elif secret_key == 'aws_session_mng':
                return get_sessionmng_secrets(secret_name, region_name)
    else:
        logger.info(f"Using local secrets for {secret_key}.")
        return _load_secret_local(local_secrets, secret_key)
    

def _load_secret_local(local_secrets, secret_key):
    """Load secrets from local file"""
    logger.info(f"Loading {secret_key} from local secrets file.")
    try:
        # Access the nested 'local_development' object
        local_dev = local_secrets.get('local_development', {})

        if secret_key == 'aws_secret_name':
            if isinstance(local_dev.get('openai_api_key'), str):
                logger.info("Local secret for openai_api_key loaded successfully.")
                return {
                    'openai_api_key': local_dev.get('openai_api_key', ''),
                    'anthropic_api_key': local_dev.get('anthropic_api_key', ''),
                    'llm_provider': local_dev.get('llm_provider', 'openai')
                }
        elif secret_key == 'aws_session_mng':
            if isinstance(local_dev.get('session_mng'), str):
                logger.info("Local secret for session_mng loaded successfully.")
                return {'sessionmng_key': local_dev.get('session_mng', '')}
        logger.info(f"No local secret found for {secret_key}.")
        return {}
    except Exception as e:
        logger.info(f"Warning: Could not load {secret_key} from local secrets file: {str(e)}")
        return {}
        

class Config:
    """Application configuration"""

    # flag indicating local or AWS S3 storage
    USE_AWS_STORAGE = False
    USE_AWS_SECRETS = True


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

    # Load configs 
    _config_dir = os.path.dirname(__file__)
    _aws_config = _load_json_file(os.path.join(_config_dir, 'aws_secrets_config.json'))

    # AWS Secrets Manager configuration
    AWS_REGION = _aws_config.get('aws_region')
    AWS_SECRET_NAME = _aws_config.get('aws_secret_name')

    _local_secrets = _load_json_file(os.path.join(_config_dir, 'secrets_config.json'))
    _llm_config = _load_json_file(os.path.join(_config_dir, 'llm_config.json'))
    _llm_secrets = _load_secret(USE_AWS_SECRETS,_aws_config, _local_secrets,'aws_secret_name')
    _sessionmng_secrets = _load_secret(USE_AWS_SECRETS,_aws_config,_local_secrets,'aws_session_mng')

    # LLM API keys
    OPENAI_API_KEY = _llm_secrets.get('openai_api_key', '')
    ANTHROPIC_API_KEY = _llm_secrets.get('anthropic_api_key', '')
    LLM_PROVIDER = _llm_secrets.get('llm_provider', 'openai')

    @staticmethod
    def get_llm_model_config(provider=None):
        """Get LLM model configuration for a specific provider"""
        if provider is None:
            provider = Config._llm_secrets.get('llm_provider', 'openai')
        return Config._llm_config.get(provider, Config._llm_config.get('openai', {}))

    
    # secret key for session management
    SECRET_KEY = _sessionmng_secrets.get('sessionmng_key', '')

# Default configuration to use
config = Config()
