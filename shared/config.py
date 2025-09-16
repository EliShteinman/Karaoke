"""
Central configuration for HebKaraoke project
Contains configuration classes for all services
"""

import os
from typing import Optional


class BaseServiceConfig:
    """Base configuration class for all services"""

    def __init__(self, service_name: str):
        self.service_name = service_name

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with service prefix"""
        return os.getenv(f"{self.service_name.upper()}_{key}", default)


class KafkaConfig(BaseServiceConfig):
    """Configuration for Kafka connection and topics"""

    def __init__(self):
        super().__init__("KAFKA")

        # Connection settings
        self.bootstrap_servers = self.get_env("BOOTSTRAP_SERVERS", "localhost:9092")

        # Topic names for the project
        self.topic_song_download_requested = self.get_env("TOPIC_DOWNLOAD_REQUESTED", "song.download.requested")
        self.topic_song_downloaded = self.get_env("TOPIC_DOWNLOADED", "song.downloaded")
        self.topic_audio_process_requested = self.get_env("TOPIC_AUDIO_PROCESS", "audio.process.requested")
        self.topic_audio_vocals_processed = self.get_env("TOPIC_VOCALS_PROCESSED", "audio.vocals_processed")
        self.topic_transcription_requested = self.get_env("TOPIC_TRANSCRIPTION", "transcription.process.requested")
        self.topic_transcription_done = self.get_env("TOPIC_TRANSCRIPTION_DONE", "transcription.done")

        # Consumer group IDs
        self.consumer_group_youtube = self.get_env("CONSUMER_GROUP_YOUTUBE", "youtube-service")
        self.consumer_group_audio = self.get_env("CONSUMER_GROUP_AUDIO", "audio-service")
        self.consumer_group_transcription = self.get_env("CONSUMER_GROUP_TRANSCRIPTION", "transcription-service")


class ElasticsearchConfig(BaseServiceConfig):
    """Configuration for Elasticsearch connection and indices"""

    def __init__(self):
        super().__init__("ELASTICSEARCH")

        # Connection settings
        self.scheme = self.get_env("SCHEME", "http")
        self.host = self.get_env("HOST", "localhost")
        self.port = int(self.get_env("PORT", "9200"))
        self.username = self.get_env("USERNAME")
        self.password = self.get_env("PASSWORD")

        # Index names
        self.songs_index = self.get_env("SONGS_INDEX", "songs")
        self.logs_index = self.get_env("LOGS_INDEX", "logs")

    @property
    def url(self) -> str:
        """Get the full Elasticsearch URL"""
        return f"{self.scheme}://{self.host}:{self.port}"


class FileStorageConfig(BaseServiceConfig):
    """Configuration for file storage"""

    def __init__(self):
        super().__init__("STORAGE")

        # Storage settings
        self.base_path = self.get_env("BASE_PATH", "/shared")
        self.storage_type = self.get_env("TYPE", "volume")  # volume, s3, etc.

        # S3 settings (for future use)
        self.s3_bucket = self.get_env("S3_BUCKET")
        self.s3_region = self.get_env("S3_REGION", "us-east-1")
        self.s3_access_key = self.get_env("S3_ACCESS_KEY")
        self.s3_secret_key = self.get_env("S3_SECRET_KEY")


class LoggerConfig(BaseServiceConfig):
    """Configuration for logging"""

    def __init__(self):
        super().__init__("LOG")

        # Logging settings
        self.level = self.get_env("LEVEL", "INFO")
        self.format = self.get_env("FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Elasticsearch logging
        self.elasticsearch_enabled = self.get_env("ELASTICSEARCH_ENABLED", "true").lower() == "true"
        self.elasticsearch_scheme = self.get_env("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_host = self.get_env("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(self.get_env("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_index = self.get_env("ELASTICSEARCH_INDEX", "logs")

    @property
    def elasticsearch_url(self) -> str:
        """Get the full Elasticsearch URL for logging"""
        return f"{self.elasticsearch_scheme}://{self.elasticsearch_host}:{self.elasticsearch_port}"


class YouTubeServiceConfig(BaseServiceConfig):
    """Configuration for YouTube service"""

    def __init__(self):
        super().__init__("YOUTUBE")

        # YouTube API
        self.api_key = self.get_env("API_KEY")
        self.max_results = int(self.get_env("MAX_RESULTS", "10"))

        # Download settings
        self.download_quality = self.get_env("DOWNLOAD_QUALITY", "bestaudio")
        self.download_format = self.get_env("DOWNLOAD_FORMAT", "mp3")


class AudioServiceConfig(BaseServiceConfig):
    """Configuration for Audio processing service"""

    def __init__(self):
        super().__init__("AUDIO")

        # Processing settings
        self.vocal_removal_method = self.get_env("VOCAL_REMOVAL_METHOD", "spleeter")
        self.output_format = self.get_env("OUTPUT_FORMAT", "mp3")
        self.sample_rate = int(self.get_env("SAMPLE_RATE", "44100"))
        self.bitrate = self.get_env("BITRATE", "128k")


class TranscriptionServiceConfig(BaseServiceConfig):
    """Configuration for Transcription service"""

    def __init__(self):
        super().__init__("TRANSCRIPTION")

        # STT settings
        self.model_name = self.get_env("MODEL_NAME", "whisper-base")
        self.language = self.get_env("LANGUAGE", "auto")
        self.output_format = self.get_env("OUTPUT_FORMAT", "lrc")


class APIServerConfig(BaseServiceConfig):
    """Configuration for API server"""

    def __init__(self):
        super().__init__("API")

        # Server settings
        self.host = self.get_env("HOST", "0.0.0.0")
        self.port = int(self.get_env("PORT", "8000"))
        self.debug = self.get_env("DEBUG", "false").lower() == "true"

        # CORS settings
        self.cors_origins = self.get_env("CORS_ORIGINS", "*").split(",")


class StreamlitClientConfig(BaseServiceConfig):
    """Configuration for Streamlit client"""

    def __init__(self):
        super().__init__("STREAMLIT")

        # App settings
        self.title = self.get_env("TITLE", "HebKaraoke")
        self.theme = self.get_env("THEME", "dark")

        # API connection
        self.api_base_url = self.get_env("API_BASE_URL", "http://localhost:8000")


class ProjectConfig:
    """
    Central configuration for the entire HebKaraoke project
    Contains all service configurations
    """

    def __init__(self):
        # Service configurations
        self.kafka = KafkaConfig()
        self.elasticsearch = ElasticsearchConfig()
        self.storage = FileStorageConfig()
        self.logger = LoggerConfig()
        self.youtube = YouTubeServiceConfig()
        self.audio = AudioServiceConfig()
        self.transcription = TranscriptionServiceConfig()
        self.api = APIServerConfig()
        self.streamlit = StreamlitClientConfig()

        # Project metadata
        self.project_name = os.getenv("PROJECT_NAME", "HebKaraoke")
        self.version = os.getenv("PROJECT_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")

    def get_service_config(self, service_name: str):
        """Get configuration for a specific service"""
        return getattr(self, service_name.lower(), None)

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


# Global configuration instance
config = ProjectConfig()

# Convenience accessors for commonly used configs
kafka_config = config.kafka
elasticsearch_config = config.elasticsearch
storage_config = config.storage
logger_config = config.logger