"""
Function logger - logs function calls to file
Tracks timestamp, user_name, and function called
"""
import os
import sys
from datetime import datetime
from functools import wraps
from loguru import logger

# Global variable for singleton instance
_function_logger = None


class FunctionLogger:
    """Logging feature for function calls"""
    _initialized = False  # Class variable for singleton pattern

    def __init__(self, log_dir='data/logs'):
        if FunctionLogger._initialized:
            return

        # Ensures the log directory exists
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.log_file = os.path.join(log_dir, 'detailed.log')

        # Console output - colorized
        logger.add(sys.stderr,
           format="<green>{time}</green> | <level>{message}</level>",
           colorize=True)
        # File output
        logger.add(self.log_file,
           format="{time} | {level} | {module}:{function}:{line} | {message}",
           level="DEBUG")
        # Finish initialization
        FunctionLogger._initialized = True

    def set_current_user(self, user_name):
        """Set the current user name for logging purposes"""
        self.current_user = user_name

    def get_current_user(self):
        """Get the current user name"""
        return getattr(self, 'current_user', 'Unknown')

    def log_function_call(self, function_name):
        """Log a function call"""
        logger.info(f"User: {self.get_current_user()}; Function called: {function_name}")

def get_function_logger():
    """Get the global function logger instance"""
    global _function_logger
    if _function_logger is None:
        _function_logger = FunctionLogger()
    return _function_logger


def log_function_call(func):
    """Decorator to log function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_function_logger()
        logger.log_function_call(func.__name__)
        return func(*args, **kwargs)
    return wrapper


def set_current_user(user_name):
    """Set the current user name for logging purposes"""
    logger = get_function_logger()
    logger.set_current_user(user_name)


def get_current_user():
    """Get the current user name"""
    logger = get_function_logger()
    return logger.get_current_user()


