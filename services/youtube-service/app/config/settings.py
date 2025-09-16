import os
from dotenv import load_dotenv

load_dotenv()

# Elasticsearch
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")

# Kafka
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_TOPIC_DOWNLOAD = os.getenv("KAFKA_TOPIC_DOWNLOAD", "song.downloaded")
KAFKA_TOPIC_AUDIO = os.getenv("KAFKA_TOPIC_AUDIO", "audio.process.requested")
KAFKA_TOPIC_TRANSCRIPTION = os.getenv("KAFKA_TOPIC_TRANSCRIPTION", "transcription.process.requested")

# Storage
SHARED_STORAGE_PATH = os.getenv("SHARED_STORAGE_PATH", "./shared/audio")
