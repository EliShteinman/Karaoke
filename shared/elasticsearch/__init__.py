"""
Elasticsearch package for HebKaraoke project
Provides all Elasticsearch-related functionality including configuration,
document mappings, and repositories for both sync and async operations
"""

from .config import elasticsearch_config, ElasticsearchConfig
from .elasticsearch_service import ElasticsearchService
from .elasticsearch_service_sync import ElasticsearchServiceSync
from .song_repository import SongRepository
from .song_repository_sync import SongRepositorySync
from .song_mapping import SONGS_INDEX_MAPPING, SONGS_INDEX_SETTINGS
from .generic_repository import GenericElasticsearchRepository
from .factory import ElasticsearchFactory, get_song_repository, get_elasticsearch_service

__all__ = [
    "elasticsearch_config",
    "ElasticsearchConfig",
    "ElasticsearchService",
    "ElasticsearchServiceSync",
    "SongRepository",
    "SongRepositorySync",
    "SONGS_INDEX_MAPPING",
    "SONGS_INDEX_SETTINGS",
    "GenericElasticsearchRepository",
    "ElasticsearchFactory",
    "get_song_repository",
    "get_elasticsearch_service"
]