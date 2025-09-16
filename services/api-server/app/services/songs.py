from typing import Dict, Any, Optional, List, Union

from shared.repositories.factory import RepositoryFactory
from shared.storage.file_storage import create_file_manager
from services.api_server.app.models import schemas
from services.api_server.app.config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

# --- INTERNAL LOGIC ---
def _is_song_ready(song_doc: Dict[str, Any]) -> bool:
    file_paths = song_doc.get("file_paths", {})
    return bool(file_paths.get("vocals_removed") and file_paths.get("lyrics"))

def _calculate_progress(song_doc: Dict[str, Any]) -> schemas.Progress:
    file_paths = song_doc.get("file_paths", {})
    return schemas.Progress(
        download=bool(file_paths.get("original")),
        audio_processing=bool(file_paths.get("vocals_removed")),
        transcription=bool(file_paths.get("lyrics")),
        files_ready=_is_song_ready(song_doc)
    )

# --- SERVICE FUNCTIONS ---

async def get_all_songs() -> schemas.SongsResponse:
    """Fetches all available songs from the data source."""
    try:
        logger.info("Service: Getting song repository from factory.")
        song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True) # CORRECTED CALL
        logger.info("Service: Fetching all ready songs from repository.")
        ready_songs_docs = await song_repo.get_ready_songs()
        song_list = [
            schemas.SongListItem(
                video_id=doc.get("video_id", "unknown"),  # Handle missing video_id
                title=doc.get("title", ""),
                artist=doc.get("artist", ""),
                status=doc.get("status", "unknown"),
                created_at=doc.get("created_at"),
                thumbnail=doc.get("thumbnail", ""),
                duration=doc.get("duration", 0),
                files_ready=_is_song_ready(doc)
            ) for doc in ready_songs_docs
        ]
        logger.info(f"Service: Found {len(song_list)} ready songs.")
        return schemas.SongsResponse(songs=song_list)
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred while getting all songs. Error: {e}")
        return schemas.SongsResponse(songs=[])


async def get_song_status(video_id: str) -> Optional[schemas.StatusResponse]:
    """Fetches the status of a specific song from the data source."""
    try:
        logger.info(f"Service: Getting song repository to fetch status for video_id: {video_id}.")
        song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True)
        song_doc = await song_repo.get_song(video_id)
        if not song_doc:
            logger.warning(f"Service: Song with video_id: {video_id} not found in repository.")
            return None
        logger.info(f"Service: Found document for video_id: {video_id}.")
        progress = _calculate_progress(song_doc)
        return schemas.StatusResponse(
            video_id=video_id,  # Use the video_id parameter since the doc doesn't include it
            status=song_doc.get("status", "unknown"),
            progress=progress
        )
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred for video_id: {video_id}. Error: {e}")
        return None

async def create_song_zip_file(video_id: str) -> Optional[bytes]:
    """Creates an in-memory ZIP package with the song's assets."""
    try:
        logger.info(f"Service: Creating file manager for ZIP creation for video_id: {video_id}.")
        file_manager = create_file_manager(base_path=settings.shared_audio_path.rsplit('/audio', 1)[0])

        if not file_manager.is_song_ready_for_karaoke(video_id):
            logger.error(f"Service: Cannot create ZIP for {video_id}. Song is not ready.")
            return None

        logger.info(f"Service: Song {video_id} is ready. Creating in-memory ZIP package.")
        zip_content = file_manager.create_karaoke_package(video_id)
        return zip_content

    except ValueError as e:
        logger.error(f"Service: Value error during ZIP creation for {video_id}. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred during ZIP creation for {video_id}. Error: {e}")
        return None