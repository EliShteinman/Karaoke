import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# YouTube API Configuration
YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME: str = os.getenv("YOUTUBE_API_SERVICE_NAME", "youtube")
YOUTUBE_API_VERSION: str = os.getenv("YOUTUBE_API_VERSION", "v3")

# Temporarily disabled for development
# if not YOUTUBE_API_KEY:
#     raise ValueError("YOUTUBE_API_KEY environment variable is required")

# Elasticsearch Configuration (using shared config format)
ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT: int = int(os.getenv("ELASTICSEARCH_PORT", 9200))
ELASTICSEARCH_SCHEME: str = os.getenv("ELASTICSEARCH_SCHEME", "http")
ELASTICSEARCH_INDEX: str = os.getenv("ELASTICSEARCH_INDEX", "songs")

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "youtube_service_group")

# Kafka Topics
KAFKA_TOPIC_SONG_DOWNLOADED: str = os.getenv("KAFKA_TOPIC_SONG_DOWNLOADED", "song.downloaded")
KAFKA_TOPIC_AUDIO_PROCESS: str = os.getenv("KAFKA_TOPIC_AUDIO_PROCESS", "audio.process.requested")
KAFKA_TOPIC_TRANSCRIPTION_PROCESS: str = os.getenv("KAFKA_TOPIC_TRANSCRIPTION_PROCESS", "transcription.process.requested")
KAFKA_TOPIC_DOWNLOAD_FAILED: str = os.getenv("KAFKA_TOPIC_DOWNLOAD_FAILED", "song.download.failed")

# Storage Configuration
SHARED_STORAGE_PATH: str = os.getenv("SHARED_STORAGE_PATH", "./data/audio")

# YTDLP Configuration
YTDLP_OUTPUT_TEMPLATE: str = os.getenv("YTDLP_OUTPUT_TEMPLATE", "/shared/audio/%(id)s/original.%(ext)s")
YTDLP_AUDIO_FORMAT: str = os.getenv("YTDLP_AUDIO_FORMAT", "mp3")
YTDLP_AUDIO_QUALITY: str = os.getenv("YTDLP_AUDIO_QUALITY", "128K")

# Service Configuration
SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", 8001))
SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")