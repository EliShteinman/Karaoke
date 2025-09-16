from pydantic_settings import BaseSettings
from pydantic import HttpUrl

class Settings(BaseSettings):
    """Manages application settings."""
    # Service URLs
    YOUTUBE_SERVICE_URL: HttpUrl = "http://youtube-service:8000"
    ELASTICSEARCH_URL: HttpUrl = "http://elasticsearch:9200"

    # Shared storage path
    SHARED_AUDIO_PATH: str = "/shared/audio"

    # API settings
    API_V1_STR: str = "/api/v1"

    class Config:
        # This allows loading settings from environment variables
        case_sensitive = True

# Instantiate the settings object that will be used across the application
settings = Settings()
