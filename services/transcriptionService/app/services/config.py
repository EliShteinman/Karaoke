"""
Configuration for the Transcription Service.

This file centralizes all configuration settings, loading them from environment
variables with sensible defaults for local development.
"""

import os

class TranscriptionServiceConfig:
    """
    Defines all configuration variables for the Transcription service.
    Uses: Kafka, Elasticsearch, Storage, and service-specific settings.
    """

    # --- Kafka Configuration ---
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_TRANSCRIPTION", "transcription-service-group")
    kafka_topic_transcription_requested = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_REQUESTED", "transcription.process.requested")
    kafka_topic_transcription_done = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_DONE", "transcription.done")
    kafka_topic_transcription_failed = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_FAILED", "transcription.failed")

    # --- Elasticsearch Configuration ---
    elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
    elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
    elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

    # --- Storage Configuration ---
    storage_base_path = os.getenv("STORAGE_BASE_PATH", "./data/audio")

    # --- Service-Specific Settings: Speech-to-Text Model ---
    stt_model_name = os.getenv("STT_MODEL_NAME", "large-v3")
    stt_device = os.getenv("STT_DEVICE", "cpu")
    stt_compute_type = os.getenv("STT_COMPUTE_TYPE", "int8")

    # --- Quality Control Settings ---
    # Minimum confidence threshold for accepting transcription results
    min_confidence_threshold = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.5"))

    # Preferred languages for transcription (in order of priority)
    preferred_languages = os.getenv("PREFERRED_LANGUAGES", "he,en").split(",")

    # Minimum number of segments required for valid transcription
    min_segments_required = int(os.getenv("MIN_SEGMENTS_REQUIRED", "3"))
