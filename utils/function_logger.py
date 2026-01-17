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
_s3_storage = None
_log_file_path = None

def initiliaze_logger():
    """Initialize the global function logger"""
    global _s3_storage, _log_file_path

    #setting up log directory
    log_file = os.path.join(config.DATA_DIR, 'detailed.log')
    _log_file_path = log_file

    #clear existing logs on startup
    if _clear_logs_on_startup and os.path.exists(log_file):
        os.remove(log_file)
    os.makedirs(config.DATA_DIR, exist_ok=True)

    # Console output - colorized
    logger.add(sys.stderr,
           format="<green>{time}</green> | <level>{message}</level>",
           colorize=True)

    # File output - always log locally first
    logger.add(log_file,
           format="{time} | {level} | {module}:{function}:{line} | {message}",
           level="INFO")

    # If AWS log storage is enabled, initialize S3 storage
    if config.USE_AWS_LOG_STORAGE:
        from utils.s3_storage import get_storage

        # Reuse the existing S3 storage instance (same bucket as game data)
        # This gets or creates a global storage instance using the configured bucket name
        _s3_storage = get_storage(bucket_name=config.S3_LOG_BUCKET)

        if _s3_storage.is_using_s3():
            logger.info(f"AWS log storage enabled - logs will be uploaded to S3 bucket: {_s3_storage.bucket_name}")
            logger.info("Logs will be uploaded periodically in the background and on shutdown")
        else:
            logger.warning("USE_AWS_LOG_STORAGE is True but S3_BUCKET_NAME environment variable not set")
    else:
        logger.info("AWS log storage disabled - logs saved locally only")

    # Finish initialization
    logger.info("Function logger initialized")

def upload_logs_to_s3():
    """Upload current log file to S3 (call periodically or on shutdown)"""
    global _s3_storage, _log_file_path

    if _s3_storage and _log_file_path and _s3_storage.is_using_s3():
        try:
            success = _s3_storage.upload_log_file(_log_file_path)
            if success:
                logger.info(f"Successfully uploaded logs to S3 bucket: {_s3_storage.bucket_name}")
            return success
        except Exception as e:
            # Don't crash if S3 upload fails
            logger.error(f"Failed to upload logs to S3: {e}")
            return False
    else:
        logger.debug("S3 storage not configured or log file path not set, skipping upload")
    return False

def log_function_call(func):
    """Decorator to log function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(func.__name__)
        return func(*args, **kwargs)
    return wrapper
