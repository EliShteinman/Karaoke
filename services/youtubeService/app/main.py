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

# Initialize services
youtube_service = YouTubeSearchService()
youtube_download_service = YouTubeDownloadService()

@app.get("/health")
def health_check() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}

@app.post("/search", response_model=SearchResponse)
def search_songs(payload: SearchRequest) -> SearchResponse:
    logger.info(f"Search request received: query='{payload.query}'")
    try:
        result = youtube_service.search(payload.query)
        logger.info(f"Search completed: found {len(result.results)} results")
        return result
    except Exception as e:
        logger.error(f"Search failed for query '{payload.query}': {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.post("/download", response_model=DownloadResponse)
def download_song(payload: DownloadRequest) -> DownloadResponse:
    logger.info(f"Download request received: video_id='{payload.video_id}'")
    try:
        result = youtube_download_service.download(
            video_id=payload.video_id,
            title=payload.title,
            channel=payload.channel,
            duration=payload.duration,
            thumbnail=payload.thumbnail
        )
        logger.info(f"Download completed: video_id='{payload.video_id}', status='{result.status}'")
        return result
    except Exception as e:
        logger.error(f"Download failed for video_id='{payload.video_id}': {e}")
        raise HTTPException(status_code=500, detail="Download failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT,
    )