"""
Central configuration for HebKaraoke project
Contains self-contained configuration classes for all services
Each service config class defines ALL environment variables it needs explicitly
"""

import os
from typing import Optional


class APIServerConfig:
    """Configuration for API Server service - self-contained"""

    def __init__(self):
        # Server settings
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("API_DEBUG", "false").lower() == "true"

        # CORS settings
        self.cors_origins = os.getenv("API_CORS_ORIGINS", "*").split(",")

        # Infrastructure dependencies this service needs
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")


class YouTubeServiceConfig:
    """Configuration for YouTube service - self-contained"""

    def __init__(self):
        # Critical API key - no default value, must be provided
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")

        # Service-specific settings
        self.max_results = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))
        self.download_quality = os.getenv("YOUTUBE_DOWNLOAD_QUALITY", "bestaudio")
        self.download_format = os.getenv("YOUTUBE_DOWNLOAD_FORMAT", "mp3")

        # Infrastructure dependencies this service needs
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_YOUTUBE", "youtube-service")
        self.kafka_topic_download_requested = os.getenv("KAFKA_TOPIC_DOWNLOAD_REQUESTED", "song.download.requested")
        self.kafka_topic_song_downloaded = os.getenv("KAFKA_TOPIC_SONG_DOWNLOADED", "song.downloaded")

        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")


class AudioServiceConfig:
    """Configuration for Audio Processing service - self-contained"""

    def __init__(self):
        # Service-specific settings
        self.vocal_removal_method = os.getenv("AUDIO_VOCAL_REMOVAL_METHOD", "spleeter")
        self.output_format = os.getenv("AUDIO_OUTPUT_FORMAT", "mp3")
        self.sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
        self.bitrate = os.getenv("AUDIO_BITRATE", "128k")

        # Infrastructure dependencies this service needs
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_AUDIO", "audio-service")
        self.kafka_topic_audio_process_requested = os.getenv("KAFKA_TOPIC_AUDIO_PROCESS_REQUESTED", "audio.process.requested")
        self.kafka_topic_vocals_processed = os.getenv("KAFKA_TOPIC_VOCALS_PROCESSED", "audio.vocals_processed")

        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")


class TranscriptionServiceConfig:
    """Configuration for Transcription service - self-contained"""

    def __init__(self):
        # Service-specific settings
        self.model_name = os.getenv("TRANSCRIPTION_MODEL_NAME", "whisper-base")
        self.language = os.getenv("TRANSCRIPTION_LANGUAGE", "auto")
        self.output_format = os.getenv("TRANSCRIPTION_OUTPUT_FORMAT", "lrc")

        # Infrastructure dependencies this service needs
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_TRANSCRIPTION", "transcription-service")
        self.kafka_topic_transcription_requested = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_REQUESTED", "transcription.process.requested")
        self.kafka_topic_transcription_done = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_DONE", "transcription.done")

        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")


class StreamlitClientConfig:
    """Configuration for Streamlit client - self-contained"""

    def __init__(self):
        # Client-specific settings
        self.title = os.getenv("STREAMLIT_TITLE", "HebKaraoke")
        self.theme = os.getenv("STREAMLIT_THEME", "dark")

        # API connection
        self.api_base_url = os.getenv("STREAMLIT_API_BASE_URL", "http://localhost:8000")


class ProjectConfig:
    """
    Central configuration for the entire HebKaraoke project
    Contains all service configurations with self-contained service configs
    """

    def __init__(self):
        # Service configurations - each is self-contained
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


# Global configuration instance
config = ProjectConfig()