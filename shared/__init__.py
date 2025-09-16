"""
Shared package for HebKaraoke project
Contains all shared components: Kafka, Elasticsearch, file storage, and utilities

Import from specific submodules:
- from shared.kafka import KafkaProducerAsync, KafkaConsumerSync
- from shared.elasticsearch import get_song_repository, elasticsearch_config
- from shared.storage import create_file_manager, KaraokeFileManager
- from shared.utils import Logger
- from shared.config import config

This package does not export anything at the root level to avoid unnecessary dependencies.
Each service can import only what it needs.
"""

# No exports at root level - import from submodules directly
__all__ = []