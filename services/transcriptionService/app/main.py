import os
import signal
import sys
import time
import traceback
from threading import Event

# Load environment variables first to ensure all modules have access to them
from dotenv import load_dotenv
load_dotenv()

# This line prevents a Windows-specific error related to symlinks when downloading models.
# It must be set before importing libraries that use huggingface_hub (e.g., faster_whisper).
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ["CT2_VERBOSE"] = "0"

# Now, import our own modules
from shared.utils.logger import Logger
from services.transcriptionService.app.consumers.transcriptionConsumer import TranscriptionConsumer

# Initialize logger
from services.transcriptionService.app.services.config import TranscriptionServiceConfig
logger = TranscriptionServiceConfig.initialize_logger()

# Global shutdown event for graceful service termination
shutdown_event = Event()

def signal_handler(signum, _frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received shutdown signal: {signum}")
    shutdown_event.set()

def run_consumer_with_retry(max_retries: int = 5, retry_delay: int = 5) -> None:
    """
    Run the transcription consumer with automatic retry on failures

    Args:
        max_retries: Maximum number of consecutive failures before giving up
        retry_delay: Delay in seconds between retry attempts
    """
    consecutive_failures = 0

    while not shutdown_event.is_set() and consecutive_failures < max_retries:
        consumer = None
        try:
            logger.info("Initializing TranscriptionConsumer...")
            consumer = TranscriptionConsumer()

            logger.info("Starting consumer service...")
            consumer.start()

            # If we reach this point, the consumer stopped gracefully
            logger.info("Consumer stopped gracefully")
            consecutive_failures = 0  # Reset failure counter on successful run
            break

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            shutdown_event.set()
            break

        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Consumer failure #{consecutive_failures}: {e}")
            logger.debug(f"Consumer failure traceback: {traceback.format_exc()}")

            if consecutive_failures < max_retries:
                logger.warning(f"Retrying in {retry_delay} seconds... ({consecutive_failures}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logger.critical(f"Maximum retry attempts ({max_retries}) exceeded. Service will shut down.")
                break

        finally:
            # Ensure consumer is properly cleaned up
            if consumer and hasattr(consumer, 'shutdown'):
                try:
                    consumer.shutdown()
                except Exception as cleanup_error:
                    logger.error(f"Error during consumer cleanup: {cleanup_error}")

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("==================================================")
    logger.info("=== Starting Transcription Service... ===")
    logger.info("==================================================")

    try:
        run_consumer_with_retry()

    except Exception as e:
        logger.critical(f"Unhandled error in main service loop: {e}")
        logger.critical(f"Main service error traceback: {traceback.format_exc()}")
        sys.exit(1)

    finally:
        logger.info("==================================================")
        logger.info("=== Transcription Service has been shut down. ===")
        logger.info("==================================================")
