"""
Utility modules for the Life Game application
"""
from .aws_secrets import SecretsManager, get_secrets_manager

__all__ = ['SecretsManager', 'get_secrets_manager']
