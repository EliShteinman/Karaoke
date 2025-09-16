"""
Elasticsearch package for HebKaraoke project - Generic Infrastructure Layer
Provides generic Elasticsearch services and tools that are reusable across projects
"""

from .elasticsearch_service import ElasticsearchService
from .elasticsearch_service_sync import ElasticsearchServiceSync
from .song_mapping import SONGS_INDEX_MAPPING, SONGS_INDEX_SETTINGS
from .generic_repository import GenericElasticsearchRepository
from .factory import ElasticsearchFactory, get_song_repository, get_elasticsearch_service

__all__ = [
    "ElasticsearchService",
    "ElasticsearchServiceSync",
    "SONGS_INDEX_MAPPING",
    "SONGS_INDEX_SETTINGS",
    "GenericElasticsearchRepository",
    "ElasticsearchFactory",
    "get_song_repository",
    "get_elasticsearch_service"
]