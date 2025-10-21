"""
Logging configuration module with support for verbose mode.

This module sets up structured logging for the entire application,
supporting both file and console output with configurable verbosity.
"""

import logging
import os
from pathlib import Path
from typing import Optional


# ANSI color codes for terminal output
class ColorCodes:
    """ANSI escape codes for colored terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Log level colors
    DEBUG = '\033[36m'      # Cyan
    INFO = '\033[32m'       # Green
    WARNING = '\033[33m'    # Yellow
    ERROR = '\033[31m'      # Red
    CRITICAL = '\033[35m'   # Magenta


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color to log messages based on level.

    Colors are only applied to terminal output, not to file logs.
    """

    LEVEL_COLORS = {
        logging.DEBUG: ColorCodes.DEBUG,
        logging.INFO: ColorCodes.INFO,
        logging.WARNING: ColorCodes.WARNING,
        logging.ERROR: ColorCodes.ERROR,
        logging.CRITICAL: ColorCodes.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with appropriate colors."""
        # Get the color for this log level
        color = self.LEVEL_COLORS.get(record.levelno, ColorCodes.RESET)

        # Save the original levelname
        original_levelname = record.levelname

        # Apply color to the level name
        record.levelname = f"{color}{record.levelname}{ColorCodes.RESET}"

        # Format the message
        formatted = super().format(record)

        # Restore original levelname for potential other handlers
        record.levelname = original_levelname

        return formatted


class AppLogger:
    """
    Application logger with support for verbose mode and file output.

    The logger writes to both console and file, with different formatting
    and levels based on the verbose flag.
    """

    def __init__(self, name: str = "ecom_cs_agent", verbose: bool = False):
        """
        Initialize the application logger.

        Args:
            name: Logger name (default: "ecom_cs_agent")
            verbose: Enable verbose/debug mode (default: False)
        """
        self.logger = logging.getLogger(name)
        self.verbose = verbose

        # Clear any existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Set level based on verbose flag
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler - always debug level for troubleshooting
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler - level based on verbose flag
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

        # Different formatting for verbose vs normal mode with color support
        if verbose:
            console_formatter = ColoredFormatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
        else:
            # Simpler format for normal mode with color
            console_formatter = ColoredFormatter('%(levelname)s: %(message)s')

        console_handler.setFormatter(console_formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False

    def get_logger(self) -> logging.Logger:
        """Return the configured logger instance."""
        return self.logger

    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self.verbose


def setup_logger(verbose: bool = False, log_level: Optional[str] = None) -> logging.Logger:
    """
    Setup and return a configured logger instance.

    Args:
        verbose: Enable verbose/debug output
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    app_logger = AppLogger(verbose=verbose)
    logger = app_logger.get_logger()

    # Override log level if specified
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)

    return logger
