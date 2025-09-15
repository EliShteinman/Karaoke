"""
הגדרות שירות הורדה
"""

import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    הגדרות השירות
    """

    # Kafka settings
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "downloader-service"

    # MongoDB settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "hebkaraoke"

    # Elasticsearch settings
    elasticsearch_host: str = "localhost"
    elasticsearch_port: int = 9200

    # Service settings
    service_name: str = "downloader"
    service_port: int = 8000

    # YouTube-DL settings
    output_format: str = "wav"
    audio_quality: str = "best"
    sample_rate: int = 16000

    class Config:
        env_file = ".env"


settings = Settings()