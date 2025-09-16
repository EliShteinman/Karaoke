import os

# This line prevents a Windows-specific error related to symlinks when downloading models.
# It must be set before importing libraries that use huggingface_hub (e.g., faster_whisper).
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from .consumers.transcriptionConsumer import TranscriptionConsumer
from dotenv import load_dotenv

os.environ["CT2_VERBOSE"] = "0"
load_dotenv()

if __name__ == "__main__":
    consumer = TranscriptionConsumer()
    consumer.start()
