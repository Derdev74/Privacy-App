"""
Centralized logging configuration for the Privacy Data Deletion Tool.
Provides consistent logging across all modules with file and console output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with color support for console output.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        # Add color to log level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(log_level=logging.INFO, log_to_file=True, log_dir='logs'):
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_dir: Directory to store log files

    Returns:
        logging.Logger: Configured root logger
    """
    # Create logs directory if it doesn't exist
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Create log filename with timestamp
        log_filename = log_path / f"privacy_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (detailed format)
    if log_to_file:
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    return root_logger


# Create a default logger instance for imports
logger = logging.getLogger('privacy_tool')

# Set default level (will be overridden by setup_logging)
logger.setLevel(logging.INFO)

# Add a basic console handler if setup_logging hasn't been called yet
if not logger.handlers:
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(_console_handler)


# Convenience functions for quick logging
def debug(message, *args, **kwargs):
    """Log a debug message."""
    logger.debug(message, *args, **kwargs)


def info(message, *args, **kwargs):
    """Log an info message."""
    logger.info(message, *args, **kwargs)


def warning(message, *args, **kwargs):
    """Log a warning message."""
    logger.warning(message, *args, **kwargs)


def error(message, *args, **kwargs):
    """Log an error message."""
    logger.error(message, *args, **kwargs)


def critical(message, *args, **kwargs):
    """Log a critical message."""
    logger.critical(message, *args, **kwargs)


def exception(message, *args, **kwargs):
    """Log an exception with traceback."""
    logger.exception(message, *args, **kwargs)


if __name__ == "__main__":
    # Test the logger
    print("="*60)
    print("LOGGER TEST")
    print("="*60)

    setup_logging(log_level=logging.DEBUG, log_to_file=True)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Caught an exception")

    print("\n" + "="*60)
    print("Logger test complete! Check logs/ directory for log file.")
    print("="*60)
