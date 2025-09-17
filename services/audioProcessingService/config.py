"""
Configuration for the Audio Processing Service.

This file centralizes all configuration settings, loading them from environment
variables with sensible defaults for local development.
"""

import os
from pathlib import Path


class AudioProcessingServiceConfig:
    """
    Defines all configuration variables for the Audio Processing service.
    Uses: Kafka, Elasticsearch, Storage, and service-specific settings.
    """

    # --- Kafka Configuration ---
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_AUDIO", "audio-processing-service-group")
    kafka_topic_audio_requested = os.getenv("KAFKA_TOPIC_AUDIO_REQUESTED", "audio.process.requested")
    kafka_topic_audio_processed = os.getenv("KAFKA_TOPIC_AUDIO_PROCESSED", "audio.vocals_processed")
    kafka_topic_audio_failed = os.getenv("KAFKA_TOPIC_AUDIO_FAILED", "audio.processing.failed")

    # --- Elasticsearch Configuration ---
    elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
    elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
    elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

    # --- Storage Configuration ---
    storage_base_path = os.getenv("STORAGE_BASE_PATH", "data")

    # --- Service-Specific Settings: Audio Processing ---
    # Demucs model to use for vocal separation
    demucs_model_name = os.getenv("DEMUCS_MODEL_NAME", "htdemucs")

    # Audio processing device (cpu/cuda)
    processing_device = os.getenv("PROCESSING_DEVICE", "cpu")

    # Maximum processing time per file (minutes)
    max_processing_time_minutes = int(os.getenv("MAX_PROCESSING_TIME_MINUTES", "15"))

    # Temporary directory for processing
    temp_processing_dir = os.getenv("TEMP_PROCESSING_DIR", str(Path("tmp") / "audio_processing"))

    # --- Quality Control Settings ---
    # Minimum output file size as percentage of input (to detect processing failures)
    min_output_size_ratio = float(os.getenv("MIN_OUTPUT_SIZE_RATIO", "0.05"))  # 5%

    # Maximum output file size as percentage of input (to detect abnormal results)
    max_output_size_ratio = float(os.getenv("MAX_OUTPUT_SIZE_RATIO", "1.5"))   # 150%

    # --- Audio Format Settings ---
    # Output audio format
    output_format = os.getenv("OUTPUT_FORMAT", "mp3")

    # Output audio bitrate
    output_bitrate = os.getenv("OUTPUT_BITRATE", "128k")

    # Sample rate for processing
    sample_rate = int(os.getenv("SAMPLE_RATE", "44100"))

    # Number of audio channels
    channels = int(os.getenv("CHANNELS", "2"))

    # --- Performance Settings ---
    # Number of concurrent processing jobs
    max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))

    # Memory limit per processing job (MB)
    memory_limit_mb = int(os.getenv("MEMORY_LIMIT_MB", "2048"))

    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that all required configuration values are properly set.
        Returns True if valid, raises ValueError if invalid.
        """
        # Validate paths exist or can be created
        try:
            Path(cls.temp_processing_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create temp processing directory: {e}")

        # Validate numeric ranges
        if not (0.01 <= cls.min_output_size_ratio <= 1.0):
            raise ValueError("min_output_size_ratio must be between 0.01 and 1.0")

        if not (1.0 <= cls.max_output_size_ratio <= 10.0):
            raise ValueError("max_output_size_ratio must be between 1.0 and 10.0")

        if cls.max_processing_time_minutes < 1:
            raise ValueError("max_processing_time_minutes must be at least 1")

        if cls.sample_rate not in [22050, 44100, 48000]:
            raise ValueError("sample_rate must be one of: 22050, 44100, 48000")

        if cls.channels not in [1, 2]:
            raise ValueError("channels must be 1 (mono) or 2 (stereo)")

        return True