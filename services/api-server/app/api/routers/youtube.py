from fastapi import APIRouter, HTTPException, status
import httpx
from ...models import schemas
from ...clients import youtube_service_client
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

router = APIRouter()


@router.post("/search", response_model=schemas.SearchResponse)
async def search_youtube(search_request: schemas.SearchRequest):
    """Endpoint to search for songs. Forwards the request to the YouTube service."""
    logger.info(f"Router: Received search request for query: '{search_request.query}'")
    try:
        logger.info(f"Router: Forwarding search request to YouTube Service for query: '{search_request.query}'")
        response = await youtube_service_client.post("/search", json=search_request.dict())
        response.raise_for_status()  # Raises an exception for 4xx/5xx responses
        logger.info("Router: Successfully received search results from YouTube Service.")
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Router: Could not connect to YouTube Service. Error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="YouTube Service is unavailable.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Router: YouTube Service returned an error status {e.response.status_code}. Response: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
    except Exception as e:
        logger.error(f"Router: An unexpected error occurred during search forwarding. Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")


@router.post("/download", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.DownloadResponse)
async def queue_download(download_request: schemas.DownloadRequest):
    """Endpoint to queue a song for download. Forwards the request to the YouTube service."""
    logger.info(f"Router: Received download request for video_id: {download_request.video_id}")
    try:
        logger.info(f"Router: Forwarding download request to YouTube Service for video_id: {download_request.video_id}")
        response = await youtube_service_client.post("/download", json=download_request.dict())
        response.raise_for_status()
        logger.info(f"Router: Successfully received '202 Accepted' from YouTube Service for video_id: {download_request.video_id}")
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Router: Could not connect to YouTube Service. Error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="YouTube Service is unavailable.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Router: YouTube Service returned an error status {e.response.status_code}. Response: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
    except Exception as e:
        logger.error(f"Router: An unexpected error occurred during download forwarding. Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")
