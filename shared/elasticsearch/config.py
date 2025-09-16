"""
Elasticsearch configuration - now uses the central config system
This file is maintained for backwards compatibility
"""

from typing import Union

from elasticsearch import AsyncElasticsearch, Elasticsearch

from ..config import elasticsearch_config as central_es_config


class ElasticsearchConfig:
    """
    Configuration for Elasticsearch connection
    Wraps the central config for backwards compatibility
    """

    def __init__(self):
        # Use central config
        self._central_config = central_es_config

    @property
    def scheme(self) -> str:
        return self._central_config.scheme

    @property
    def host(self) -> str:
        return self._central_config.host

    @property
    def port(self) -> int:
        return self._central_config.port

    @property
    def username(self) -> str:
        return self._central_config.username

    @property
    def password(self) -> str:
        return self._central_config.password

    @property
    def songs_index(self) -> str:
        return self._central_config.songs_index

    @property
    def logs_index(self) -> str:
        return self._central_config.logs_index

    @property
    def url(self) -> str:
        """Get the full Elasticsearch URL"""
        return self._central_config.url

    def get_async_client(self) -> AsyncElasticsearch:
        """Create and return an AsyncElasticsearch client"""
        client_config = {"hosts": [self.url]}

        if self.username and self.password:
            client_config["basic_auth"] = (self.username, self.password)

        return AsyncElasticsearch(**client_config)

    def get_sync_client(self) -> Elasticsearch:
        """Create and return a sync Elasticsearch client"""
        client_config = {"hosts": [self.url]}

        if self.username and self.password:
            client_config["basic_auth"] = (self.username, self.password)

        return Elasticsearch(**client_config)

    def get_client(self, async_mode: bool = True) -> Union[AsyncElasticsearch, Elasticsearch]:
        """
        Create and return an Elasticsearch client

        Args:
            async_mode: If True, returns AsyncElasticsearch, else Elasticsearch
        """
        if async_mode:
            return self.get_async_client()
        else:
            return self.get_sync_client()

    def get_connection_info(self) -> dict:
        """Get connection info for logging (without sensitive data)"""
        return {
            "url": self.url,
            "songs_index": self.songs_index,
            "logs_index": self.logs_index,
            "has_auth": bool(self.username and self.password),
        }


# Global config instance
elasticsearch_config = ElasticsearchConfig()