"""
Configuration file for the Life Game application
"""
import secrets
import os
import json


class Config:
    """Application configuration"""

    # Flask secret key for session management
    # IMPORTANT: Change this to a secure random string in production
    SECRET_KEY = 'your-secret-key-change-this'

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

    # Configuration files
    _secrets_config = None
    _secrets_config_path = os.path.join(os.path.dirname(__file__), 'secrets_config.json')
    _llm_config = None
    _llm_config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')

    @classmethod
    def _load_secrets_config(cls):
        """Load configuration from secrets_config.json"""
        if cls._secrets_config is not None:
            return cls._secrets_config

        try:
            with open(cls._secrets_config_path, 'r') as f:
                cls._secrets_config = json.load(f)
                return cls._secrets_config
        except FileNotFoundError:
            print(f"Warning: secrets_config.json not found at {cls._secrets_config_path}")
            print("Using default configuration")
            cls._secrets_config = {
                'use_aws_secrets': True,
                'aws_region': 'us-east-1',
                'aws_secret_name': 'life-game/llm-api-keys',
                'local_development': {
                    'openai_api_key': '',
                    'anthropic_api_key': '',
                    'llm_provider': 'openai'
                }
            }
            return cls._secrets_config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in secrets_config.json: {e}")
            raise

    # AWS Secrets Manager configuration (from secrets_config.json)
    @classmethod
    @property
    def AWS_REGION(cls):
        config = cls._load_secrets_config()
        return config.get('aws_region', 'us-east-1')

    @classmethod
    @property
    def AWS_SECRET_NAME(cls):
        config = cls._load_secrets_config()
        return config.get('aws_secret_name', 'life-game/llm-api-keys')

    @classmethod
    @property
    def USE_AWS_SECRETS(cls):
        config = cls._load_secrets_config()
        return config.get('use_aws_secrets', True)

    # LLM API Configuration
    # These will be loaded from AWS Secrets Manager if use_aws_secrets is True
    # Otherwise, use local_development values from secrets_config.json
    _llm_secrets = None

    @classmethod
    def _load_llm_secrets(cls):
        """Load LLM secrets from AWS Secrets Manager or secrets_config.json"""
        if cls._llm_secrets is not None:
            return cls._llm_secrets

        secrets_config = cls._load_secrets_config()

        if secrets_config.get('use_aws_secrets', True):
            try:
                from aws_secrets import get_llm_secrets
                aws_region = secrets_config.get('aws_region', 'us-east-1')
                secret_name = secrets_config.get('aws_secret_name', 'life-game/llm-api-keys')
                cls._llm_secrets = get_llm_secrets(secret_name, aws_region)
                return cls._llm_secrets
            except Exception as e:
                print(f"Warning: Could not load from AWS Secrets Manager: {e}")
                print("Falling back to local_development configuration")

        # Use local_development from secrets_config.json
        local_dev = secrets_config.get('local_development', {})
        cls._llm_secrets = {
            'openai_api_key': local_dev.get('openai_api_key', ''),
            'anthropic_api_key': local_dev.get('anthropic_api_key', ''),
            'llm_provider': local_dev.get('llm_provider', 'openai')
        }
        return cls._llm_secrets

    @property
    def OPENAI_API_KEY(self):
        """Get OpenAI API key from AWS Secrets Manager or environment"""
        secrets = self.__class__._load_llm_secrets()
        return secrets.get('openai_api_key', '')

    @property
    def ANTHROPIC_API_KEY(self):
        """Get Anthropic API key from AWS Secrets Manager or environment"""
        secrets = self.__class__._load_llm_secrets()
        return secrets.get('anthropic_api_key', '')

    @property
    def LLM_PROVIDER(self):
        """Get LLM provider from AWS Secrets Manager or secrets_config.json"""
        secrets = self.__class__._load_llm_secrets()
        return secrets.get('llm_provider', 'openai')

    # LLM Model Configuration
    @classmethod
    def _load_llm_config(cls):
        """Load LLM model configuration from llm_config.json"""
        if cls._llm_config is not None:
            return cls._llm_config

        try:
            with open(cls._llm_config_path, 'r') as f:
                cls._llm_config = json.load(f)
                return cls._llm_config
        except FileNotFoundError:
            print(f"Warning: llm_config.json not found at {cls._llm_config_path}")
            print("Using default LLM configuration")
            cls._llm_config = {
                'openai': {
                    'model': 'gpt-4o-mini',
                    'max_tokens': 150,
                    'temperature': 0.7,
                    'top_p': 1.0,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                },
                'anthropic': {
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 150,
                    'temperature': 0.7,
                    'top_p': 1.0
                }
            }
            return cls._llm_config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in llm_config.json: {e}")
            raise

    @classmethod
    def get_llm_model_config(cls, provider=None):
        """
        Get LLM model configuration for a specific provider

        Args:
            provider: 'openai' or 'anthropic' (defaults to current provider)

        Returns:
            dict: Model configuration parameters
        """
        config = cls._load_llm_config()
        if provider is None:
            # Use the configured provider from secrets
            secrets = cls._load_llm_secrets()
            provider = secrets.get('llm_provider', 'openai')

        return config.get(provider, config.get('openai', {}))

    @staticmethod
    def generate_secret_key():
        """Generate a secure random secret key"""
        return secrets.token_hex(32)

    @classmethod
    def reload_secrets(cls):
        """Force reload of secrets and config from files (useful for testing)"""
        cls._llm_secrets = None
        cls._secrets_config = None
        cls._llm_config = None
        secrets_config = cls._load_secrets_config()
        if secrets_config.get('use_aws_secrets', True):
            try:
                from aws_secrets import get_secrets_manager
                aws_region = secrets_config.get('aws_region', 'us-east-1')
                secrets_manager = get_secrets_manager(aws_region)
                secrets_manager.clear_cache()
            except Exception:
                pass


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
