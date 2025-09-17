"""
Configuration for Audio Processing Service

This module contains all configuration parameters for the audio processing service.
All values should eventually be moved to environment variables for production deployment.
"""

import os

# Elasticsearch Configuration
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ES_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
ES_SCHEME = os.getenv("ELASTICSEARCH_SCHEME", "http")
ES_INDEX = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

# Kafka Configuration
TOPICS = [os.getenv("KAFKA_AUDIO_TOPIC", "audio.process.requested")]
GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "audio_processing_service_group")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Service Configuration
SERVICE_NAME = "audio_processing_service"
MAX_PROCESSING_TIME_MINUTES = int(os.getenv("MAX_PROCESSING_TIME_MINUTES", "15"))
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/audio_processing")

# Audio Processing Configuration
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "2"))
AUDIO_BIT_DEPTH = int(os.getenv("AUDIO_BIT_DEPTH", "16"))
MIN_QUALITY_THRESHOLD = float(os.getenv("MIN_QUALITY_THRESHOLD", "0.1"))  # 10% of original size minimum
