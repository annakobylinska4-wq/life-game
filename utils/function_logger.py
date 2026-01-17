"""
Function logger - logs function calls to file
Tracks timestamp, user_name, and function called
"""
import os
import sys
from functools import wraps
from loguru import logger
from config.config import config

_clear_logs_on_startup = True

def initiliaze_logger():
    """Initialize the global function logger""" 
        
    #setting up log directory
    log_file = os.path.join(config.DATA_DIR, 'detailed.log')
    #clear existing logs on startup
    if _clear_logs_on_startup and os.path.exists(log_file):
        os.remove(log_file)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    # Console output - colorized
    logger.add(sys.stderr,
           format="<green>{time}</green> | <level>{message}</level>",
           colorize=True)
        # File output
    logger.add(log_file,
           format="{time} | {level} | {module}:{function}:{line} | {message}",
           level="DEBUG")
    # Finish initialization
    logger.info("Function logger initialized")

def log_function_call(func):
    """Decorator to log function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(func.__name__)
        return func(*args, **kwargs)
    return wrapper
