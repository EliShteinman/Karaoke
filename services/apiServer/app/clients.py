import httpx
from typing import Optional, Dict, Any
from services.apiServer.app.config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(name="api-server-clients")

# YouTube Service HTTP Client
youtube_service_client: httpx.AsyncClient = httpx.AsyncClient(
    base_url=settings.youtube_service_url,
    timeout=10.0  # Quick timeout - we expect immediate 202 response
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
        except httpx.TimeoutException as e:
            logger.error(f"Search request timed out for query '{query}': {e}")
            raise
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to YouTube Service for search: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"YouTube Service returned error {e.response.status_code} for search: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search request: {e}")
            raise

    async def download(self, video_data: dict) -> Optional[dict]:
        """Request video download via YouTube Service."""
        try:
            video_id = video_data.get('video_id', 'unknown')
            logger.info(f"Sending download request to YouTube Service for video_id: {video_id}")
            response = await self.client.post("/download", json=video_data)
            response.raise_for_status()
            logger.info(f"Download request completed successfully for video_id: {video_id}")
            return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Download request timed out for video_id '{video_id}': {e}")
            raise
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to YouTube Service for download: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"YouTube Service returned error {e.response.status_code} for download: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during download request: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("YouTube Service client closed")


# Global client instance
youtube_client = YouTubeServiceClient(settings.youtube_service_url)
