"""
AWS Secrets Manager integration
Retrieves secrets from AWS Secrets Manager for LLM API keys
"""
import json
import boto3
from botocore.exceptions import ClientError
from loguru import logger

class SecretsManager:
    """Handles retrieval of secrets from AWS Secrets Manager"""

    def __init__(self, region_name=None):
        """
        Initialize the Secrets Manager client

        Args:
            region_name: AWS region (defaults to us-east-1)
        """
        self.region_name = region_name or 'us-east-1'
        self.client = None
        self._cache = {}

    def _get_client(self):
        """Lazy initialization of boto3 client"""
        if self.client is None:
            self.client = boto3.client('secretsmanager', region_name=self.region_name)
        return self.client

    def get_secret(self, secret_name):
        """
        Retrieve a secret from AWS Secrets Manager

        Args:
            secret_name: Name of the secret in AWS Secrets Manager

        Returns:
            dict: The secret value as a dictionary (if JSON) or string

        Raises:
            ClientError: If the secret cannot be retrieved
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]

        try:
            client = self._get_client()
            response = client.get_secret_value(SecretId=secret_name)

            # Secrets can be stored as either SecretString or SecretBinary
            if 'SecretString' in response:
                secret = response['SecretString']
                try:
                    # Try to parse as JSON
                    secret_dict = json.loads(secret)
                    self._cache[secret_name] = secret_dict
                    return secret_dict
                except json.JSONDecodeError:
                    # If not JSON, return as string
                    self._cache[secret_name] = secret
                    return secret
            else:
                # Binary secrets (less common for API keys)
                secret = response['SecretBinary']
                self._cache[secret_name] = secret
                return secret

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Secret '{secret_name}' not found in AWS Secrets Manager")
            elif error_code == 'InvalidRequestException':
                raise Exception(f"Invalid request for secret '{secret_name}'")
            elif error_code == 'InvalidParameterException':
                raise Exception(f"Invalid parameter for secret '{secret_name}'")
            elif error_code == 'DecryptionFailure':
                raise Exception(f"Cannot decrypt secret '{secret_name}'")
            elif error_code == 'InternalServiceError':
                raise Exception(f"AWS Secrets Manager internal error for '{secret_name}'")
            else:
                raise Exception(f"Error retrieving secret '{secret_name}': {str(e)}")

    def get_secret_value(self, secret_name, key=None):
        """
        Get a specific value from a secret

        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            key: Optional key to extract from JSON secret

        Returns:
            The secret value (entire secret or specific key)
        """
        secret = self.get_secret(secret_name)

        if key and isinstance(secret, dict):
            return secret.get(key, '')

        return secret if not isinstance(secret, dict) else secret

    def clear_cache(self):
        """Clear the secrets cache"""
        self._cache = {}


# Global instance
_secrets_manager = None


def get_secrets_manager(region_name=None):
    """
    Get or create the global SecretsManager instance

    Args:
        region_name: AWS region (optional)

    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(region_name)
    return _secrets_manager


def get_llm_secrets(secret_name='life-game/llm-api-keys', region_name=None):
    """
    Retrieve LLM API keys from AWS Secrets Manager

    Expected secret format (JSON):
    {
        "openai_api_key": "sk-...",
        "anthropic_api_key": "sk-ant-...",
        "llm_provider": "openai"
    }

    Args:
        secret_name: Name of the secret containing LLM API keys
        region_name: AWS region (optional, uses default if not specified)

    Returns:
        dict: Dictionary with 'openai_api_key', 'anthropic_api_key', 'llm_provider'
    """
    
    logger.debug(f"Retrieving LLM secrets from AWS Secrets Manager: {secret_name} in region {region_name}")

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
    logger.debug(f"Retrieving SessionMng secrets from AWS Secrets Manager: {secret_name} in region {region_name}")
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
        