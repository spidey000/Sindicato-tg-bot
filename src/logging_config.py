import logging
import logging.handlers
import os
import sys
from src.config import LOG_LEVEL

def setup_logging():
    """
    Configures the logging system with:
    1. Console Handler: Prints logs to stdout (Terminal).
    2. File Handler: Saves logs to 'logs/bot.log' with rotation.
    3. Error Handler: Saves ERROR/CRITICAL logs to 'logs/error.log'.
    """
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define Log Level
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # Formatters
    # Console: Clean and readable
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File: Detailed context (Filename, Line Number)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # 2. General File Handler (Rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "bot.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)  # Capture INFO and above in files

    # 3. Error File Handler
    error_file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setFormatter(file_formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Root Logger Configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything at root, let handlers filter

    # Remove default handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)

    # Suppress noisy external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("google.auth").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.info("✅ Logging system initialized. Logs directory: %s", os.path.abspath(log_dir))
