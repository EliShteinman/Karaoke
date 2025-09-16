"""
Factory for creating Elasticsearch services and repositories
Provides a unified interface to create either sync or async instances
"""

from typing import Union

from elasticsearch import AsyncElasticsearch, Elasticsearch

from shared.elasticsearch.elasticsearch_service import ElasticsearchService
from shared.elasticsearch.elasticsearch_service_sync import ElasticsearchServiceSync
from shared.repositories.song_repository import SongRepository
from shared.repositories.song_repository_sync import SongRepositorySync


class ElasticsearchFactory:
    """
    Factory class to create Elasticsearch services and repositories
    Generic factory that receives connection parameters from external config
    """

    @staticmethod
    def create_song_repository(
        elasticsearch_host: str = "localhost",
        elasticsearch_port: int = 9200,
        elasticsearch_scheme: str = "http",
        elasticsearch_username: str = None,
        elasticsearch_password: str = None,
        songs_index: str = "songs",
        async_mode: bool = True
    ) -> Union[SongRepository, SongRepositorySync]:
        """
        Create a song repository with provided connection parameters

        Args:
            elasticsearch_host: Elasticsearch host
            elasticsearch_port: Elasticsearch port
            elasticsearch_scheme: http or https
            elasticsearch_username: Optional username
            elasticsearch_password: Optional password
            songs_index: Name of songs index
            async_mode: If True, creates async repository, else sync repository

        Returns:
            SongRepository (async) or SongRepositorySync (sync)
        """
        # Build connection config
        hosts = [f"{elasticsearch_scheme}://{elasticsearch_host}:{elasticsearch_port}"]
        client_config = {"hosts": hosts}

        if elasticsearch_username and elasticsearch_password:
            client_config["basic_auth"] = (elasticsearch_username, elasticsearch_password)

        if async_mode:
            # Create async versions
            es_client = AsyncElasticsearch(**client_config)
            es_service = ElasticsearchService(es_client, songs_index)
            return SongRepository(es_service)
        else:
            # Create sync versions
            es_client = Elasticsearch(**client_config)
            es_service = ElasticsearchServiceSync(es_client, songs_index)
            return SongRepositorySync(es_service)

    @staticmethod
    def create_elasticsearch_service(
        index_name: str,
        elasticsearch_host: str = "localhost",
        elasticsearch_port: int = 9200,
        elasticsearch_scheme: str = "http",
        elasticsearch_username: str = None,
        elasticsearch_password: str = None,
        async_mode: bool = True
    ) -> Union[ElasticsearchService, ElasticsearchServiceSync]:
        """
        Create an Elasticsearch service for any index with provided connection parameters

        Args:
            index_name: Name of the Elasticsearch index
            elasticsearch_host: Elasticsearch host
            elasticsearch_port: Elasticsearch port
            elasticsearch_scheme: http or https
            elasticsearch_username: Optional username
            elasticsearch_password: Optional password
            async_mode: If True, creates async service, else sync service

        Returns:
            ElasticsearchService (async) or ElasticsearchServiceSync (sync)
        """
        # Build connection config
        hosts = [f"{elasticsearch_scheme}://{elasticsearch_host}:{elasticsearch_port}"]
        client_config = {"hosts": hosts}

        if elasticsearch_username and elasticsearch_password:
            client_config["basic_auth"] = (elasticsearch_username, elasticsearch_password)

        if async_mode:
            es_client = AsyncElasticsearch(**client_config)
            return ElasticsearchService(es_client, index_name)
        else:
            es_client = Elasticsearch(**client_config)
            return ElasticsearchServiceSync(es_client, index_name)


# Convenience functions for direct usage with default local development settings
def get_song_repository(async_mode: bool = True) -> Union[SongRepository, SongRepositorySync]:
    """Get a song repository with default local settings (async by default)"""
    return ElasticsearchFactory.create_song_repository(async_mode=async_mode)


def get_elasticsearch_service(
    index_name: str, async_mode: bool = True
) -> Union[ElasticsearchService, ElasticsearchServiceSync]:
    """Get an Elasticsearch service for any index with default local settings (async by default)"""
    return ElasticsearchFactory.create_elasticsearch_service(index_name, async_mode=async_mode)