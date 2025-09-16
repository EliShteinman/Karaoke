import os

class APIServerConfig:
    """
    Configuration for the API Server, based on the project's template.
    Loads settings from environment variables.
    """
    def __init__(self):
        # --- Service-specific settings ---
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        self.cors_origins = os.getenv("API_CORS_ORIGINS", "*").split(",")

        # --- Elasticsearch Configuration ---
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")


        # --- Other Service URLs ---
        # This was missing from the template but is required by the API server
        self.youtube_service_url = os.getenv("YOUTUBE_SERVICE_URL", "http://youtube-service:8000")

        # --- Shared Paths ---
        # Renamed from storage_base_path to match previous implementation
        self.shared_audio_path = os.getenv("SHARED_AUDIO_PATH", "/shared/audio")

# Instantiate the settings object that will be used across the application
# The rest of the application imports `settings` from this module.
settings = APIServerConfig()
