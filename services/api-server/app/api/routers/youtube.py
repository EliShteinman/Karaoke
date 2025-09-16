from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import httpx

from ...models import schemas
# from ...clients import youtube_service_client # UNCOMMENT THIS LINE TO ACTIVATE REAL IMPLEMENTATION
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

router = APIRouter()

# TODO: This function can be removed when the real implementation is activated.
async def fake_forward_to_youtube_service(*, endpoint: str, data: dict):
    """This function simulates forwarding a request to the YouTube service."""
    logger.info(f"Forwarding request to YouTube Service at endpoint: {endpoint} (SIMULATED)")
    return True

@router.post("/search", response_model=schemas.SearchResponse)
async def search_youtube(search_request: schemas.SearchRequest):
    """Endpoint to search for songs. Forwards the request to the YouTube service."""
    logger.info(f"Router: Received search request for query: '{search_request.query}'")

    # # TODO: REAL IMPLEMENTATION - UNCOMMENT THIS BLOCK AND REMOVE THE FAKE ONE
    # try:
    #     logger.info(f"Router: Forwarding search request to YouTube Service for query: '{search_request.query}'")
    #     response = await youtube_service_client.post("/search", json=search_request.dict())
    #     response.raise_for_status()  # Raises an exception for 4xx/5xx responses
    #     logger.info("Router: Successfully received search results from YouTube Service.")
    #     return response.json()
    # except httpx.RequestError as e:
    #     logger.error(f"Router: Could not connect to YouTube Service. Error: {e}")
    #     raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="YouTube Service is unavailable.")
    # except httpx.HTTPStatusError as e:
    #     logger.error(f"Router: YouTube Service returned an error status {e.response.status_code}. Response: {e.response.text}")
    #     raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
    # except Exception as e:
    #     logger.error(f"Router: An unexpected error occurred during search forwarding. Error: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")

    # --- FAKE IMPLEMENTATION (CURRENTLY ACTIVE) ---
    await fake_forward_to_youtube_service(endpoint="/search", data=search_request.dict())
    fake_results = schemas.SearchResponse(
        results=[
            schemas.SearchResult(
                video_id="dQw4w9WgXcQ",
                title="Rick Astley - Never Gonna Give You Up",
                channel="RickAstleyVEVO",
                duration=213,
                thumbnail="https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                published_at=datetime.now()
            )
        ]
    )
    logger.info("Router: Returning hardcoded search results.")
    return fake_results

@router.post("/download", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.DownloadResponse)
async def queue_download(download_request: schemas.DownloadRequest):
    """Endpoint to queue a song for download. Forwards the request to the YouTube service."""
    logger.info(f"Router: Received download request for video_id: {download_request.video_id}")

    # # TODO: REAL IMPLEMENTATION - UNCOMMENT THIS BLOCK AND REMOVE THE FAKE ONE
    # try:
    #     logger.info(f"Router: Forwarding download request to YouTube Service for video_id: {download_request.video_id}")
    #     response = await youtube_service_client.post("/download", json=download_request.dict())
    #     response.raise_for_status()
    #     logger.info(f"Router: Successfully received '202 Accepted' from YouTube Service for video_id: {download_request.video_id}")
    #     return response.json()
    # except httpx.RequestError as e:
    #     logger.error(f"Router: Could not connect to YouTube Service. Error: {e}")
    #     raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="YouTube Service is unavailable.")
    # except httpx.HTTPStatusError as e:
    #     logger.error(f"Router: YouTube Service returned an error status {e.response.status_code}. Response: {e.response.text}")
    #     raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
    # except Exception as e:
    #     logger.error(f"Router: An unexpected error occurred during download forwarding. Error: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")

    # --- FAKE IMPLEMENTATION (CURRENTLY ACTIVE) ---
    await fake_forward_to_youtube_service(endpoint="/download", data=download_request.dict())
    response = schemas.DownloadResponse(
        status="accepted",
        video_id=download_request.video_id,
        message="Song queued for processing via YouTube Service."
    )
    logger.info(f"Router: Responding with 202 Accepted for video_id: {download_request.video_id}")
    return response
