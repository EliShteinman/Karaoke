from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from services.youtubeService.app.models.youtube_models import (
    SearchRequest, SearchResponse,
    DownloadRequest, DownloadResponse
)
from services.youtubeService.app.services.youtube_search import YouTubeSearchService
from services.youtubeService.app.services.youtube_download import YouTubeDownloadService
from services.youtubeService.app.config.config import config
from shared.utils.logger import Logger

app = FastAPI(title="YouTube Service")

# Initialize shared logger with proper configuration
logger_config = config.get_logger_config()
logger = Logger.get_logger(**logger_config)

# Initialize services with error handling
youtube_service = None
youtube_download_service = None

try:
    youtube_service = YouTubeSearchService()
    youtube_download_service = YouTubeDownloadService()
    logger.info("YouTube services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize YouTube services: {e}")
    logger.warning("YouTube Service will start but API endpoints will return configuration errors")

@app.get("/health")
def health_check() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}

@app.post("/search", response_model=SearchResponse)
def search_songs(payload: SearchRequest) -> SearchResponse:
    logger.info(f"Search request received: query='{payload.query}'")
    logger.debug(f"Search request payload: {payload.model_dump(mode='json')}")

    # Check if YouTube service is properly initialized
    if youtube_service is None:
        logger.error(f"YouTube service not initialized - cannot search for '{payload.query}'")
        raise HTTPException(
            status_code=503,
            detail="YouTube service is not properly configured. Please check YouTube API key configuration."
        )

    try:
        result = youtube_service.search(payload.query)
        logger.info(f"Search completed: found {len(result.results)} results")
        return result
    except Exception as e:
        logger.error(f"Search failed for query '{payload.query}': {e}")
        # Provide more specific error message for common issues
        if "API key" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="YouTube API key is invalid or missing. Please check the service configuration."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/download", response_model=DownloadResponse, status_code=202)
def download_song(payload: DownloadRequest) -> DownloadResponse:
    logger.info(f"Download request received: video_id='{payload.video_id}'")

    # Check if YouTube download service is properly initialized
    if youtube_download_service is None:
        logger.error(f"YouTube download service not initialized - cannot download video_id='{payload.video_id}'")
        raise HTTPException(
            status_code=503,
            detail="YouTube download service is not properly configured. Please check service configuration."
        )

    try:
        # Validate request and immediately return 202 Accepted
        # Start the download process in background
        youtube_download_service.start_download_async(
            video_id=payload.video_id,
            title=payload.title,
            channel=payload.channel,
            duration=payload.duration,
            thumbnail=payload.thumbnail
        )
        logger.info(f"Download request accepted: video_id='{payload.video_id}'")
        return DownloadResponse(
            status="accepted",
            video_id=payload.video_id,
            message="Song queued for processing"
        )
    except Exception as e:
        logger.error(f"Download request failed for video_id='{payload.video_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Download request failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT,
    )