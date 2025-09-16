import os
import traceback

# Load environment variables first to ensure all modules have access to them
from dotenv import load_dotenv
load_dotenv()

# This line prevents a Windows-specific error related to symlinks when downloading models.
# It must be set before importing libraries that use huggingface_hub (e.g., faster_whisper).
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ["CT2_VERBOSE"] = "0"

# Now, import our own modules
from shared.utils.logger import Logger
from .consumers.transcriptionConsumer import TranscriptionConsumer

# Initialize logger
logger = Logger.get_logger(__name__)

if __name__ == "__main__":
    logger.info("==================================================")
    logger.info("=== Starting Transcription Service... ===")
    logger.info("==================================================")
    
    consumer = None
    try:
        consumer = TranscriptionConsumer()
        consumer.start()
    except Exception as e:
        logger.critical(f"A critical error occurred, shutting down the service. Error: {e}")
        logger.critical(traceback.format_exc())
    finally:
        # The consumer's finally block handles its own shutdown logging
        logger.info("==================================================")
        logger.info("=== Transcription Service has been shut down. ===")
        logger.info("==================================================")
