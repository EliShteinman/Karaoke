#!/usr/bin/env python3
"""
Audio Processing Service Runner

This script starts the audio processing service as a daemon process.
It handles service lifecycle, configuration validation, and graceful shutdown.
"""

import sys
import os
import signal
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.audioProcessingService.main import AudioProcessingService
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)


def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point for the audio processing service"""
    logger.info("=" * 50)
    logger.info("AUDIO PROCESSING SERVICE STARTING")
    logger.info("=" * 50)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Create and start the service
        logger.info("Initializing Audio Processing Service...")
        service = AudioProcessingService()

        logger.info("Starting service daemon...")
        service.start()  # This will run forever unless interrupted

    except Exception as e:
        logger.error(f"Failed to start Audio Processing Service: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

    logger.info("Audio Processing Service stopped")


if __name__ == "__main__":
    main()