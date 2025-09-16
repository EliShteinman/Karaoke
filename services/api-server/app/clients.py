import httpx
from elasticsearch import AsyncElasticsearch

from .config import settings

#Elasticsearch Client
es_client = AsyncElasticsearch(
    hosts=[
        {
            "host": settings.elasticsearch_host,
            "port": settings.elasticsearch_port,
            "scheme": settings.elasticsearch_scheme,
        }
    ],
    basic_auth=(
        settings.elasticsearch_username, 
        settings.elasticsearch_password
    ) if settings.elasticsearch_username else None
)

#YouTube Service HTTP Client
youtube_service_client = httpx.AsyncClient(
    base_url=settings.youtube_service_url,
    timeout=30.0
)
