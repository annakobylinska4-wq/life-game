"""
Configuration file for the Life Game application
"""
import secrets


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
