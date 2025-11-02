"""Logging configuration for the Flow Manager.

This module sets up structured logging for the application.
"""

import logging
import sys
from typing import Optional

from app.config.settings import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None
):
    """Configure application logging.
    
    Sets up logging with the specified level and format.
    If not provided, uses settings from the configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Log message format string
    """
    log_level = level or settings.log_level
    log_format = format_string or settings.log_format
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
