import os
from pathlib import Path
from typing import List, Optional


class APIServerConfig:
    """
    Centralized configuration for the API Server.
    Contains all environment variables in one place as requested.
    This is the single source for all configuration in the service.
    """

    def __init__(self) -> None:
        # --- Service-specific settings ---
        self.host: str = os.getenv("API_HOST", "0.0.0.0")
        self.port: int = int(os.getenv("API_PORT", "8000"))
        self.debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
        self.cors_origins: List[str] = os.getenv("API_CORS_ORIGINS", "*").split(",")

        # --- Elasticsearch Configuration ---
        self.elasticsearch_scheme: str = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_host: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port: int = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_songs_index: str = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")
        self.elasticsearch_username: Optional[str] = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password: Optional[str] = os.getenv("ELASTICSEARCH_PASSWORD")

        # --- External Service URLs ---
        self.youtube_service_url: str = os.getenv("YOUTUBE_SERVICE_URL", "http://youtube-service:8000")

        # --- Shared Storage Configuration ---
        self.shared_storage_base_path: str = os.getenv("SHARED_STORAGE_BASE_PATH", "data")
        self.shared_audio_path: str = os.getenv("SHARED_AUDIO_PATH", "audio")

        # --- Logging Configuration ---
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_elasticsearch_scheme: str = os.getenv("LOG_ELASTICSEARCH_SCHEME", self.elasticsearch_scheme)
        self.log_elasticsearch_host: str = os.getenv("LOG_ELASTICSEARCH_HOST", self.elasticsearch_host)
        self.log_elasticsearch_port: int = int(os.getenv("LOG_ELASTICSEARCH_PORT", str(self.elasticsearch_port)))
        self.log_elasticsearch_index: str = os.getenv("LOG_ELASTICSEARCH_INDEX", "logs")

    def get_elasticsearch_url(self) -> str:
        """Get full Elasticsearch URL for connections."""
        return f"{self.elasticsearch_scheme}://{self.elasticsearch_host}:{self.elasticsearch_port}"

    def get_log_elasticsearch_url(self) -> str:
        """Get full Elasticsearch URL for logging."""
        return f"{self.log_elasticsearch_scheme}://{self.log_elasticsearch_host}:{self.log_elasticsearch_port}"


# Instantiate the settings object that will be used across the application
# The rest of the application imports `settings` from this module.
settings = APIServerConfig()