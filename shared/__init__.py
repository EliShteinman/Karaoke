"""
Shared package for HebKaraoke project
Contains generic infrastructure tools and project-specific business logic repositories

Generic Infrastructure Layer:
- from shared.kafka import KafkaProducerAsync, KafkaConsumerSync
- from shared.elasticsearch import ElasticsearchService, ElasticsearchFactory
- from shared.storage import create_file_manager, KaraokeFileManager
- from shared.api import Logger

Project-Specific Business Logic Layer:
- from shared.repositories import SongRepository, SongRepositorySync

Configuration is now centralized in the root config.py file.
Each service should import its configuration from there.
"""

# No exports at root level - import from submodules directly
__all__ = []