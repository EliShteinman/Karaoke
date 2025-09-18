from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from services.apiServer.app.models import schemas
from services.apiServer.app.services import songs as songs_service
from shared.utils.logger import Logger

# Import config for logger initialization
from services.apiServer.app.config import settings

logger = Logger.get_logger(__name__)

router = APIRouter()

@router.get("/songs", response_model=schemas.SongsResponse)
async def get_all_songs() -> schemas.SongsResponse:
    """Endpoint to get a list of all available songs."""
    try:
        logger.info("Router: Received request for all songs.")
        logger.debug("Router: Starting to fetch all songs from service.")
        result = await songs_service.get_all_songs()
        logger.info(f"Router: Successfully retrieved {len(result.songs)} songs.")
        logger.debug(f"Router: Returning songs response with {len(result.songs)} items.")
        return result
    except Exception as e:
        logger.error(f"Router: Failed to get all songs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/songs/{video_id}/status", response_model=schemas.StatusResponse)
async def get_song_status(video_id: str) -> schemas.StatusResponse:
    """Endpoint to check the processing status of a specific song."""
    try:
        logger.info(f"Router: Received status request for video_id: {video_id}")
        logger.debug(f"Router: Starting to fetch status for video_id: {video_id}")
        status = await songs_service.get_song_status(video_id)
        if not status:
            logger.warning(f"Router: Song {video_id} not found, returning 404.")
            raise HTTPException(status_code=404, detail="Song not found")
        logger.info(f"Router: Successfully retrieved status for video_id: {video_id}, status: {status.status}")
        logger.debug(f"Router: Status response for {video_id}: {status.model_dump()}")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Router: Failed to get song status for {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/songs/{video_id}/download")
async def download_song_zip(video_id: str) -> Response:
    """Endpoint to download the ZIP file for a ready song."""
    try:
        logger.info(f"Router: Received download request for video_id: {video_id}")
        logger.debug(f"Router: Starting ZIP creation for video_id: {video_id}")
        zip_content = await songs_service.create_song_zip_file(video_id)

        if not zip_content:
            logger.error(f"Router: Could not create ZIP for {video_id}. Song not ready or not found.")
            raise HTTPException(status_code=404, detail="Song not ready or not found. Check status endpoint first.")

        logger.info(f"Router: Successfully created ZIP for video_id: {video_id}, size: {len(zip_content)} bytes")
        logger.debug(f"Router: Returning ZIP response for {video_id} with Content-Disposition header")
        # Return the ZIP file content directly
        return Response(
            content=zip_content,
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={video_id}.zip"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Router: Failed to create download for {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
