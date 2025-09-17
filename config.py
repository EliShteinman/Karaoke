"""
Configuration template for HebKaraoke project
Contains configuration classes defining ALL environment variables that shared tools require
Each service must copy the relevant class and add their own service-specific variables
This is NOT a central config file - it's a template for independent service configs
"""

import os
from pathlib import Path
from typing import Optional


class APIServerConfig:
    """
    Configuration for API Server service
    Uses: Elasticsearch (read-only)
    """

    def __init__(self):
        # Server settings - service-specific variables
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        self.cors_origins = os.getenv("API_CORS_ORIGINS", "*").split(",")

        # Elasticsearch configuration - REQUIRED by shared/elasticsearch tools
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")


class YouTubeServiceConfig:
    """
    Configuration for YouTube service
    Uses: Kafka, Elasticsearch, Storage
    """

    def __init__(self):
        # Kafka configuration - REQUIRED by shared/kafka tools
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_YOUTUBE", "youtube-service")
        self.kafka_topic_download_requested = os.getenv("KAFKA_TOPIC_DOWNLOAD_REQUESTED", "song.download.requested")
        self.kafka_topic_song_downloaded = os.getenv("KAFKA_TOPIC_SONG_DOWNLOADED", "song.downloaded")

        # Elasticsearch configuration - REQUIRED by shared/elasticsearch tools
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        # Storage configuration - REQUIRED by shared/storage tools
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", str(Path("shared")))

        # Service-specific settings - ADD THESE AS NEEDED
        # Example service-specific variables (uncomment and modify as needed):
        # self.api_key = os.getenv("YOUTUBE_API_KEY")
        # if not self.api_key:
        #     raise ValueError("YOUTUBE_API_KEY environment variable is required")
        # self.max_results = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))
        # self.download_quality = os.getenv("YOUTUBE_DOWNLOAD_QUALITY", "bestaudio")
        # self.download_format = os.getenv("YOUTUBE_DOWNLOAD_FORMAT", "mp3")


class AudioServiceConfig:
    """
    Configuration for Audio Processing service
    Uses: Kafka, Elasticsearch, Storage
    """

    def __init__(self):
        # Kafka configuration - REQUIRED by shared/kafka tools
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_AUDIO", "audio-service")
        self.kafka_topic_audio_process_requested = os.getenv("KAFKA_TOPIC_AUDIO_PROCESS_REQUESTED", "audio.process.requested")
        self.kafka_topic_vocals_processed = os.getenv("KAFKA_TOPIC_VOCALS_PROCESSED", "audio.vocals_processed")

        # Elasticsearch configuration - REQUIRED by shared/elasticsearch tools
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        # Storage configuration - REQUIRED by shared/storage tools
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", str(Path("shared")))

        # Service-specific settings - ADD THESE AS NEEDED
        # Example service-specific variables (uncomment and modify as needed):
        # self.vocal_removal_method = os.getenv("AUDIO_VOCAL_REMOVAL_METHOD", "spleeter")
        # self.output_format = os.getenv("AUDIO_OUTPUT_FORMAT", "mp3")
        # self.sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
        # self.bitrate = os.getenv("AUDIO_BITRATE", "128k")


class TranscriptionServiceConfig:
    """
    Configuration for Transcription service
    Uses: Kafka, Elasticsearch, Storage
    """

    def __init__(self):
        # Kafka configuration - REQUIRED by shared/kafka tools
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_TRANSCRIPTION", "transcription-service")
        self.kafka_topic_transcription_requested = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_REQUESTED", "transcription.process.requested")
        self.kafka_topic_transcription_done = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_DONE", "transcription.done")

        # Elasticsearch configuration - REQUIRED by shared/elasticsearch tools
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        # Storage configuration - REQUIRED by shared/storage tools
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", str(Path("shared")))

        # Service-specific settings - ADD THESE AS NEEDED
        # Example service-specific variables (uncomment and modify as needed):
        # self.model_name = os.getenv("TRANSCRIPTION_MODEL_NAME", "whisper-base")
        # self.language = os.getenv("TRANSCRIPTION_LANGUAGE", "auto")
        # self.output_format = os.getenv("TRANSCRIPTION_OUTPUT_FORMAT", "lrc")


class StreamlitClientConfig:
    """
    Configuration for Streamlit client
    Uses: HTTP connection to API Server
    """

    def __init__(self):
        # API connection - REQUIRED by shared/http tools
        self.api_base_url = os.getenv("STREAMLIT_API_BASE_URL", "http://localhost:8000")

        # Service-specific settings - ADD THESE AS NEEDED
        # Example service-specific variables (uncomment and modify as needed):
        # self.title = os.getenv("STREAMLIT_TITLE", "HebKaraoke")
        # self.theme = os.getenv("STREAMLIT_THEME", "dark")


class ProjectConfig:
    """
    Central configuration template for the entire HebKaraoke project
    Contains all service configuration templates
    Each service should copy its relevant class when deployed independently
    """

    def __init__(self):
        # Service configuration templates - each defines what shared tools require
        self.api_server = APIServerConfig()
        self.youtube_service = YouTubeServiceConfig()
        self.audio_service = AudioServiceConfig()
        self.transcription_service = TranscriptionServiceConfig()
        self.streamlit_client = StreamlitClientConfig()

        # Project metadata
        self.project_name = os.getenv("PROJECT_NAME", "HebKaraoke")
        self.version = os.getenv("PROJECT_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


# Global configuration instance for development
# In production, each service creates its own config based on the relevant class above
config = ProjectConfig()