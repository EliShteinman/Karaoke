from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import zipfile
from shared.repositories.factory import RepositoryFactory
from shared.storage.file_storage import create_file_manager
from ..models import schemas
from ..config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(
    name="api-server-services",
    es_url=f"{settings.elasticsearch_scheme}://{settings.elasticsearch_host}:{settings.elasticsearch_port}",
    index="logs"
)


# --- INTERNAL LOGIC ---
def _is_song_ready(song_doc: Dict[str, Any]) -> bool:
    """Check if song has both required files for karaoke."""
    file_paths = song_doc.get("file_paths", {})
    vocals_removed = file_paths.get("vocals_removed")
    lyrics = file_paths.get("lyrics")
    return bool(
        vocals_removed and lyrics and
        vocals_removed.strip() and lyrics.strip()
    )

def _calculate_progress(song_doc: Dict[str, Any]) -> schemas.Progress:
    """Calculate processing progress for a song based on file paths."""
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
        song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True)
        logger.info("Service: Fetching all ready songs from repository.")
        ready_songs_docs = await song_repo.get_ready_songs()

        song_list = []
        for doc in ready_songs_docs:
            try:
                song_item = schemas.SongListItem(
                    video_id=doc.get("video_id", ""),
                    title=doc.get("title", ""),
                    artist=doc.get("artist", ""),
                    status=doc.get("status", ""),
                    created_at=doc.get("created_at"),
                    thumbnail=doc.get("thumbnail", ""),
                    duration=doc.get("duration", 0),
                    files_ready=_is_song_ready(doc)
                )
                song_list.append(song_item)
            except Exception as song_error:
                logger.error(f"Service: Failed to process song document {doc.get('video_id', 'unknown')}: {song_error}")
                continue

        logger.info(f"Service: Found {len(song_list)} ready songs.")
        return schemas.SongsResponse(songs=song_list)
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred while getting all songs. Error: {e}")
        raise

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
            video_id=song_doc["video_id"],
            status=song_doc["status"],
            progress=progress
        )
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred for video_id: {video_id}. Error: {e}")
        raise

async def create_song_zip_file(video_id: str) -> Optional[bytes]:
    """Creates an in-memory ZIP package with the song's assets."""
    try:
        logger.info(f"Service: Creating file manager for ZIP creation for video_id: {video_id}.")
        base_path = settings.shared_audio_path.rsplit('/audio', 1)[0] if '/audio' in settings.shared_audio_path else "/shared"
        file_manager = create_file_manager(storage_type="volume", base_path=base_path)

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
