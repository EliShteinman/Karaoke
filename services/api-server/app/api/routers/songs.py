from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from services.api_server.app.models import schemas
from services.api_server.app.services import songs as songs_service
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

router = APIRouter()

@router.get("/songs", response_model=schemas.SongsResponse)
async def get_all_songs() -> schemas.SongsResponse:
    """Endpoint to get a list of all available songs."""
    logger.info("Router: Received request for all songs.")
    return await songs_service.get_all_songs()

@router.get("/songs/{video_id}/status", response_model=schemas.StatusResponse)
async def get_song_status(video_id: str) -> schemas.StatusResponse:
    """Endpoint to check the processing status of a specific song."""
    logger.info(f"Router: Received status request for video_id: {video_id}")
    status = await songs_service.get_song_status(video_id)
    if not status:
        logger.warning(f"Router: Song {video_id} not found, returning 404.")
        raise HTTPException(status_code=404, detail="Song not found")
    return status

@router.get("/songs/{video_id}/download")
async def download_song_zip(video_id: str) -> Response:
    """Endpoint to download the ZIP file for a ready song."""
    logger.info(f"Router: Received download request for video_id: {video_id}")
    zip_content = await songs_service.create_song_zip_file(video_id)

    if not zip_content:
        logger.error(f"Router: Could not create ZIP for {video_id}. Song not ready or not found.")
        raise HTTPException(status_code=404, detail="Song not ready or not found. Check status endpoint first.")

    # Return the ZIP file content directly
    return Response(
        content=zip_content,
        media_type='application/zip',
        headers={"Content-Disposition": f"attachment; filename={video_id}.zip"}
    )
