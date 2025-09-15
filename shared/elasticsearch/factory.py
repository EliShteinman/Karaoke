"""
Factory for creating Elasticsearch services and repositories
Provides a unified interface to create either sync or async instances
"""

from typing import Union

from .config import elasticsearch_config
from .elasticsearch_service import ElasticsearchService
from .elasticsearch_service_sync import ElasticsearchServiceSync
from .song_repository import SongRepository
from .song_repository_sync import SongRepositorySync


class ElasticsearchFactory:
    """
    Factory class to create Elasticsearch services and repositories
    Similar to Kafka's approach - you decide sync/async at runtime
    """

    @staticmethod
    def create_song_repository(async_mode: bool = True) -> Union[SongRepository, SongRepositorySync]:
        """
        Create a song repository

        Args:
            async_mode: If True, creates async repository, else sync repository

        Returns:
            SongRepository (async) or SongRepositorySync (sync)
        """
        if async_mode:
            # Create async versions
            es_client = elasticsearch_config.get_async_client()
            es_service = ElasticsearchService(es_client, elasticsearch_config.songs_index)
            return SongRepository(es_service)
        else:
            # Create sync versions
            es_client = elasticsearch_config.get_sync_client()
            es_service = ElasticsearchServiceSync(es_client, elasticsearch_config.songs_index)
            return SongRepositorySync(es_service)

    @staticmethod
    def create_elasticsearch_service(
        index_name: str, async_mode: bool = True
    ) -> Union[ElasticsearchService, ElasticsearchServiceSync]:
        """
        Create an Elasticsearch service for any index

        Args:
            index_name: Name of the Elasticsearch index
            async_mode: If True, creates async service, else sync service

        Returns:
            ElasticsearchService (async) or ElasticsearchServiceSync (sync)
        """
        if async_mode:
            es_client = elasticsearch_config.get_async_client()
            return ElasticsearchService(es_client, index_name)
        else:
            es_client = elasticsearch_config.get_sync_client()
            return ElasticsearchServiceSync(es_client, index_name)


# Convenience functions for direct usage
def get_song_repository(async_mode: bool = True) -> Union[SongRepository, SongRepositorySync]:
    """Get a song repository (async by default)"""
    return ElasticsearchFactory.create_song_repository(async_mode)


def get_elasticsearch_service(
    index_name: str, async_mode: bool = True
) -> Union[ElasticsearchService, ElasticsearchServiceSync]:
    """Get an Elasticsearch service for any index (async by default)"""
    return ElasticsearchFactory.create_elasticsearch_service(index_name, async_mode)