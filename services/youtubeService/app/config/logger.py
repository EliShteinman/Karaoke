"""
YouTube Service Logger Configuration
Uses the shared logger from the shared library
"""
from shared.utils.logger import Logger


def get_logger(name: str):
    """
    Get logger instance using shared logger
    This function is maintained for backward compatibility
    but now uses the shared logger infrastructure
    """
    return Logger.get_logger(f"youtube_service.{name}")


# Export the main logger getter for easy access
logger = Logger.get_logger("youtube_service")