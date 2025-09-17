"""
YouTube Service - Unified Configuration
All configuration settings for the YouTube service in one place
"""
import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class YouTubeServiceConfig:
    """
    Centralized configuration for YouTube Service
    Includes all service-specific and infrastructure settings
    """

    # ===== YouTube API Configuration =====
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    YOUTUBE_API_SERVICE_NAME: str = os.getenv("YOUTUBE_API_SERVICE_NAME", "youtube")
    YOUTUBE_API_VERSION: str = os.getenv("YOUTUBE_API_VERSION", "v3")

    # Temporarily disabled for development
    # if not YOUTUBE_API_KEY:
    #     raise ValueError("YOUTUBE_API_KEY environment variable is required")

    # ===== Elasticsearch Configuration =====
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT: int = int(os.getenv("ELASTICSEARCH_PORT", 9200))
    ELASTICSEARCH_SCHEME: str = os.getenv("ELASTICSEARCH_SCHEME", "http")
    ELASTICSEARCH_INDEX: str = os.getenv("ELASTICSEARCH_INDEX", "songs")

    # Elasticsearch URL for easy access
    ELASTICSEARCH_URL: str = f"{ELASTICSEARCH_SCHEME}://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"

    # ===== Logging Configuration =====
    LOG_LEVEL: int = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
    LOG_ELASTICSEARCH_SCHEME: str = os.getenv("LOG_ELASTICSEARCH_SCHEME", ELASTICSEARCH_SCHEME)
    LOG_ELASTICSEARCH_HOST: str = os.getenv("LOG_ELASTICSEARCH_HOST", ELASTICSEARCH_HOST)
    LOG_ELASTICSEARCH_PORT: int = int(os.getenv("LOG_ELASTICSEARCH_PORT", ELASTICSEARCH_PORT))
    LOG_ELASTICSEARCH_INDEX: str = os.getenv("LOG_ELASTICSEARCH_INDEX", "logs")

    # Logging Elasticsearch URL
    LOG_ELASTICSEARCH_URL: str = f"{LOG_ELASTICSEARCH_SCHEME}://{LOG_ELASTICSEARCH_HOST}:{LOG_ELASTICSEARCH_PORT}"

    # ===== Kafka Configuration =====
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "youtube_service_group")

    # ===== Kafka Topics =====
    KAFKA_TOPIC_SONG_DOWNLOADED: str = os.getenv("KAFKA_TOPIC_SONG_DOWNLOADED", "song.downloaded")
    KAFKA_TOPIC_AUDIO_PROCESS: str = os.getenv("KAFKA_TOPIC_AUDIO_PROCESS", "audio.process.requested")
    KAFKA_TOPIC_TRANSCRIPTION_PROCESS: str = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_PROCESS", "transcription.process.requested")
    KAFKA_TOPIC_DOWNLOAD_FAILED: str = os.getenv("KAFKA_TOPIC_DOWNLOAD_FAILED", "song.download.failed")

    # ===== Storage Configuration =====
    SHARED_STORAGE_PATH: str = os.getenv("SHARED_STORAGE_PATH", "data")

    # ===== YTDLP Configuration =====
    YTDLP_OUTPUT_TEMPLATE: str = os.getenv("YTDLP_OUTPUT_TEMPLATE", str(Path("data") / "audio" / "%(id)s" / "original.%(ext)s"))
    YTDLP_AUDIO_FORMAT: str = os.getenv("YTDLP_AUDIO_FORMAT", "wav")
    YTDLP_AUDIO_QUALITY: str = os.getenv("YTDLP_AUDIO_QUALITY", "128K")

    # ===== YouTube Cookies Configuration =====
    YOUTUBE_COOKIES_FILE: Optional[str] = os.getenv("YOUTUBE_COOKIES_FILE")
    YOUTUBE_COOKIES_FROM_BROWSER: Optional[str] = os.getenv("YOUTUBE_COOKIES_FROM_BROWSER")  # e.g., "chrome", "firefox"

    # ===== Service Configuration =====
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", 8001))
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_NAME: str = "youtube_service"

    @classmethod
    def get_logger_config(cls) -> dict:
        """
        Get logger configuration parameters for the shared logger
        """
        return {
            "name": cls.SERVICE_NAME,
            "es_url": cls.LOG_ELASTICSEARCH_URL,
            "index": cls.LOG_ELASTICSEARCH_INDEX,
            "level": cls.LOG_LEVEL
        }

# Create a singleton config instance
config = YouTubeServiceConfig()

# Export commonly used values for backward compatibility
YOUTUBE_API_KEY = config.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = config.YOUTUBE_API_SERVICE_NAME
YOUTUBE_API_VERSION = config.YOUTUBE_API_VERSION

ELASTICSEARCH_HOST = config.ELASTICSEARCH_HOST
ELASTICSEARCH_PORT = config.ELASTICSEARCH_PORT
ELASTICSEARCH_SCHEME = config.ELASTICSEARCH_SCHEME
ELASTICSEARCH_INDEX = config.ELASTICSEARCH_INDEX

KAFKA_BOOTSTRAP_SERVERS = config.KAFKA_BOOTSTRAP_SERVERS
SHARED_STORAGE_PATH = config.SHARED_STORAGE_PATH

SERVICE_PORT = config.SERVICE_PORT
SERVICE_HOST = config.SERVICE_HOST