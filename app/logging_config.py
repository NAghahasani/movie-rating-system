"""Configuration module for application logging system."""

import logging
import sys


def setup_logging() -> logging.Logger:
    """
    Set up the standard logging configuration for the application.

    :return: Configured logger instance for movie rating system
    """
    # Use standard format: timestamp - name - level - message
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create a specific logger for the movie rating domain
    logger = logging.getLogger("movie_rating")
    logger.info("Logging system initialized successfully.")

    return logger


# Initialize global logger instance
logger = setup_logging()