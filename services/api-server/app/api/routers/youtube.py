from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from ...models import schemas
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

router = APIRouter()

# This is a fake client call. In a real scenario, this would be in a separate service file.
async def fake_forward_to_youtube_service(*, endpoint: str, data: dict):
    """This function simulates forwarding a request to the YouTube service."""
    logger.info(f"Simulating forwarding request to YouTube Service at endpoint: {endpoint}")
    # In a real app, you'd use httpx.AsyncClient here.
    # We are just pretending the call was successful.
    return True

@router.post("/search", response_model=schemas.SearchResponse)
async def search_youtube(search_request: schemas.SearchRequest):
    """Endpoint to search for songs. Forwards the request to the YouTube service."""
    logger.info(f"Router: Received search request for query: '{search_request.query}'")
    
    # Simulate forwarding and getting a response
    await fake_forward_to_youtube_service(endpoint="/search", data=search_request.dict())
    
    # Return a fake, hardcoded response that matches the schema
    fake_results = schemas.SearchResponse(
        results=[
            schemas.SearchResult(
                video_id="dQw4w9WgXcQ",
                title="(Mock) Rick Astley - Never Gonna Give You Up",
                channel="RickAstleyVEVO",
                duration=213,
                thumbnail="https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                published_at=datetime.now()
            )
        ]
    )
    logger.info("Router: Returning mock search results.")
    return fake_results

@router.post("/download", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.DownloadResponse)
async def queue_download(download_request: schemas.DownloadRequest):
    """Endpoint to queue a song for download. Forwards the request to the YouTube service."""
    logger.info(f"Router: Received download request for video_id: {download_request.video_id}")

    # Simulate forwarding the request
    await fake_forward_to_youtube_service(endpoint="/download", data=download_request.dict())

    # Return the 'Accepted' response as per the architecture
    response = schemas.DownloadResponse(
        status="accepted",
        video_id=download_request.video_id,
        message="(Mock) Song queued for processing via YouTube Service."
    )
    logger.info(f"Router: Responding with 202 Accepted for video_id: {download_request.video_id}")
    return response
