from .consumers.transcriptionConsumer import TranscriptionConsumer
from dotenv import load_dotenv
import os

os.environ["CT2_VERBOSE"] = "0"
load_dotenv()

if __name__ == "__main__":
    consumer = TranscriptionConsumer()
    consumer.start()
