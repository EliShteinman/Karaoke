import httpx
from typing import Optional
from .config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(
    name="api-server-clients",
    es_url=f"{settings.elasticsearch_scheme}://{settings.elasticsearch_host}:{settings.elasticsearch_port}",
    index="logs"
)

# YouTube Service HTTP Client
youtube_service_client: httpx.AsyncClient = httpx.AsyncClient(
    base_url=settings.youtube_service_url,
    timeout=30.0
)


class YouTubeServiceClient:
    """Client for communicating with YouTube Service."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout
        )
        logger.info(f"YouTube Service client initialized with base_url: {base_url}")

    async def search(self, query: str) -> Optional[dict]:
        """Search for videos via YouTube Service."""
        try:
            logger.info(f"Sending search request to YouTube Service for query: {query}")
            response = await self.client.post("/search", json={"query": query})
            response.raise_for_status()
            logger.info("Search request completed successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Search request failed: {e}")
            raise

    async def download(self, video_data: dict) -> Optional[dict]:
        """Request video download via YouTube Service."""
        try:
            logger.info(f"Sending download request to YouTube Service for video_id: {video_data.get('video_id')}")
            response = await self.client.post("/download", json=video_data)
            response.raise_for_status()
            logger.info("Download request completed successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Download request failed: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("YouTube Service client closed")


# Global client instance
youtube_client = YouTubeServiceClient(settings.youtube_service_url)
