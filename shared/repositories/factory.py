"""
Factory for creating project-specific repositories with configuration from central config
"""

from typing import Union

from .song_repository import SongRepository
from .song_repository_sync import SongRepositorySync
from ..elasticsearch.factory import ElasticsearchFactory


class RepositoryFactory:
    """
    Factory class for creating project-specific repositories
    Uses configuration from the centralized config system
    """

    @staticmethod
    def create_song_repository_from_config(
        service_config, async_mode: bool = True
    ) -> Union[SongRepository, SongRepositorySync]:
        """
        Create a song repository using a service configuration object
        The service config must have elasticsearch connection parameters

        Args:
            service_config: Service configuration object with elasticsearch parameters
            async_mode: If True, creates async repository, else sync repository

        Returns:
            SongRepository (async) or SongRepositorySync (sync)
        """
        return ElasticsearchFactory.create_song_repository(
            elasticsearch_host=service_config.elasticsearch_host,
            elasticsearch_port=service_config.elasticsearch_port,
            elasticsearch_scheme=service_config.elasticsearch_scheme,
            elasticsearch_username=service_config.elasticsearch_username,
            elasticsearch_password=service_config.elasticsearch_password,
            songs_index=service_config.elasticsearch_songs_index,
            async_mode=async_mode
        )

    @staticmethod
    def create_song_repository_from_params(
        elasticsearch_host: str,
        elasticsearch_port: int = 9200,
        elasticsearch_scheme: str = "http",
        elasticsearch_username: str = None,
        elasticsearch_password: str = None,
        songs_index: str = "songs",
        async_mode: bool = True
    ) -> Union[SongRepository, SongRepositorySync]:
        """
        Create a song repository with explicit parameters
        """
        return ElasticsearchFactory.create_song_repository(
            elasticsearch_host=elasticsearch_host,
            elasticsearch_port=elasticsearch_port,
            elasticsearch_scheme=elasticsearch_scheme,
            elasticsearch_username=elasticsearch_username,
            elasticsearch_password=elasticsearch_password,
            songs_index=songs_index,
            async_mode=async_mode
        )