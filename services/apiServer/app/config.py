import os
from typing import List, Optional


class APIServerConfig:
    """
    Configuration for the API Server, based on the project's template.
    Loads settings from environment variables.
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

        # --- Other Service URLs ---
        # This was missing from the template but is required by the API server
        self.youtube_service_url: str = os.getenv("YOUTUBE_SERVICE_URL", "http://youtube-service:8000")

        # --- Shared Paths ---
        # Renamed from storage_base_path to match previous implementation
        self.shared_audio_path: str = os.getenv("SHARED_AUDIO_PATH", "/shared/audio")

# Instantiate the settings object that will be used across the application
# The rest of the application imports `settings` from this module.
settings = APIServerConfig()
