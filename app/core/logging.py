import logging
import sys
import os
from logging.handlers import RotatingFileHandler

from app.core.config import get_settings

LOGGING_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(lineno)d | %(message)s"

def setup_logging() -> logging.Logger:
    settings = get_settings()
    # Map string log level to logging module's constants
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.getcwd(), "logs"))
    os.makedirs(LOG_DIR, exist_ok=True)

    LOG_FILEPATH = os.path.join(LOG_DIR, "app.log")

    # Get the specific logger
    logger = logging.getLogger(settings.app_name)
    logger.setLevel(log_level)

    # Prevent duplicate logs if setup_logging is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(LOGGING_FORMAT)

        # File Handler with rotation if enabled for local development
        if settings.enable_file_logging:
            file_handler = RotatingFileHandler(
                LOG_FILEPATH,
                maxBytes = 5 * 1024 * 1024,  # 5MB
                backupCount = 3,
                encoding = "utf-8"
                )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Disable propagation so it doesn't bubble up to the root logger
    logger.propagate = False
    
    return logger

# Initialize once at the module level or in your entry point
logger = setup_logging()
