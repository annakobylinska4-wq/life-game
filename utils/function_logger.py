"""
Function logger - logs function calls to YAML file
Tracks timestamp, user_name, and function called
"""
import os
import logging
from datetime import datetime
from functools import wraps
import threading

# Thread-local storage for current user context
_user_context = threading.local()


def set_current_user(username):
    """Set the current user for logging context"""
    _user_context.username = username


def get_current_user():
    """Get the current user from logging context"""
    return getattr(_user_context, 'username', 'unknown')


class YAMLFormatter(logging.Formatter):
    """Custom formatter that outputs log records in YAML format"""

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        user_name = getattr(record, 'user_name', 'unknown')
        function_called = getattr(record, 'function_called', record.funcName)

        yaml_entry = (
            f"- timestamp: \"{timestamp}\"\n"
            f"  user_name: \"{user_name}\"\n"
            f"  function_called: \"{function_called}\"\n"
        )
        return yaml_entry


class FunctionLogger:
    """Logger for tracking function calls in YAML format"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, log_dir='data/logs'):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_dir='data/logs'):
        if self._initialized:
            return

        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.log_file = os.path.join(log_dir, 'function_calls.yaml')

        # Create logger
        self.logger = logging.getLogger('function_logger')
        self.logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Create file handler
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)

            # Set custom YAML formatter
            formatter = YAMLFormatter()
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

        self._initialized = True

    def log_function_call(self, function_name, user_name=None):
        """Log a function call"""
        if user_name is None:
            user_name = get_current_user()

        self.logger.info(
            'function_call',
            extra={
                'user_name': user_name,
                'function_called': function_name
            }
        )


# Global logger instance
_function_logger = None


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
