from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import zipfile
# from shared.repositories.factory import RepositoryFactory # COMMENTED OUT - CIRCULAR IMPORT ISSUE IN SHARED
# from shared.storage import create_file_manager # COMMENTED OUT FOR FAKE MODE
from ..models import schemas
from ..config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

# --- FAKE DATABASE / ELASTICSEARCH DATA ---
# TODO: This entire block can be removed when the real implementation is activated.
FAKE_ELASTICSEARCH_DB: Dict[str, Dict[str, Any]] = {
    "dQw4w9WgXcQ": {
        "video_id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "artist": "Rick Astley",
        "status": "processing",
        "created_at": datetime.now(),
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "duration": 213,
        "file_paths": {
            "original": f"{settings.shared_audio_path}/dQw4w9WgXcQ/original.mp3",
            "vocals_removed": f"{settings.shared_audio_path}/dQw4w9WgXcQ/vocals_removed.mp3",
            "lyrics": f"{settings.shared_audio_path}/dQw4w9WgXcQ/lyrics.lrc"
        }
    },
    "oHg5SJYRHA0": {
        "video_id": "oHg5SJYRHA0",
        "title": "A-ha - Take On Me",
        "artist": "A-ha",
        "status": "processing",
        "created_at": datetime.now(),
        "thumbnail": "https://img.youtube.com/vi/oHg5SJYRHA0/maxresdefault.jpg",
        "duration": 225,
        "file_paths": {
            "original": f"{settings.shared_audio_path}/oHg5SJYRHA0/original.mp3",
        }
    }
}

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

    # TODO: REAL IMPLEMENTATION - UNCOMMENT THIS BLOCK AND REMOVE THE FAKE ONE
    # try:
    #     logger.info("Service: Getting song repository from factory.")
    #     song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True) # CORRECTED CALL
    #     logger.info("Service: Fetching all ready songs from repository.")
    #     ready_songs_docs = await song_repo.get_ready_songs()
    #     song_list = [
    #         schemas.SongListItem(
    #             video_id=doc.get("video_id"),
    #             title=doc.get("title"),
    #             artist=doc.get("artist"),
    #             status=doc.get("status"),
    #             created_at=doc.get("created_at"),
    #             thumbnail=doc.get("thumbnail"),
    #             duration=doc.get("duration"),
    #             files_ready=_is_song_ready(doc)
    #         ) for doc in ready_songs_docs
    #     ]
    #     logger.info(f"Service: Found {len(song_list)} ready songs.")
    #     return schemas.SongsResponse(songs=song_list)
    # except Exception as e:
    #     logger.error(f"Service: An unexpected error occurred while getting all songs. Error: {e}")
    #     return schemas.SongsResponse(songs=[])

    # --- FAKE IMPLEMENTATION (CURRENTLY ACTIVE) ---
    logger.info("Service: Fetching all songs from the local dictionary.")
    song_list = []
    for video_id, doc in FAKE_ELASTICSEARCH_DB.items():
        song_item = schemas.SongListItem(
            video_id=doc["video_id"],
            title=doc["title"],
            artist=doc["artist"],
            status=doc["status"],
            created_at=doc["created_at"],
            thumbnail=doc["thumbnail"],
            duration=doc["duration"],
            files_ready=_is_song_ready(doc)
        )
        song_list.append(song_item)
    logger.info(f"Service: Found {len(song_list)} total songs.")
    return schemas.SongsResponse(songs=song_list)

async def get_song_status(video_id: str) -> Optional[schemas.StatusResponse]:
    """Fetches the status of a specific song from the data source."""

    # TODO: REAL IMPLEMENTATION - UNCOMMENT THIS BLOCK AND REMOVE THE FAKE ONE
    # try:
    #     logger.info(f"Service: Getting song repository to fetch status for video_id: {video_id}.")
    #     song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True) # CORRECTED CALL
    #     song_doc = await song_repo.get_song(video_id)
    #     if not song_doc:
    #         logger.warning(f"Service: Song with video_id: {video_id} not found in repository.")
    #         return None
    #     logger.info(f"Service: Found document for video_id: {video_id}.")
    #     progress = _calculate_progress(song_doc)
    #     return schemas.StatusResponse(
    #         video_id=song_doc["video_id"],
    #         status=song_doc["status"],
    #         progress=progress
    #     )
    # except Exception as e:
    #     logger.error(f"Service: An unexpected error occurred for video_id: {video_id}. Error: {e}")
    #     return None

    # --- FAKE IMPLEMENTATION (CURRENTLY ACTIVE) ---
    logger.info(f"Service: Fetching status for video_id: {video_id} from local dictionary.")
    song_doc = FAKE_ELASTICSEARCH_DB.get(video_id)
    if not song_doc:
        logger.warning(f"Service: Song with video_id: {video_id} not found.")
        return None
    progress = _calculate_progress(song_doc)
    return schemas.StatusResponse(
        video_id=song_doc["video_id"],
        status=song_doc["status"],
        progress=progress
    )

async def create_song_zip_file(video_id: str) -> Optional[str]:
    """Creates an in-memory ZIP package with the song's assets."""

    # TODO: REAL IMPLEMENTATION - UNCOMMENT THIS BLOCK AND REMOVE THE FAKE ONE
    # try:
    #     logger.info(f"Service: Creating file manager for ZIP creation for video_id: {video_id}.")
    #     file_manager = create_file_manager(base_path=settings.shared_audio_path.rsplit('/audio', 1)[0]) # CORRECTED CALL
    #
    #     if not file_manager.is_song_ready_for_karaoke(video_id):
    #         logger.error(f"Service: Cannot create ZIP for {video_id}. Song is not ready.")
    #         return None
    #
    #     logger.info(f"Service: Song {video_id} is ready. Creating in-memory ZIP package.")
    #     zip_content = file_manager.create_karaoke_package(video_id)
    #     return zip_content
    #
    # except ValueError as e:
    #     logger.error(f"Service: Value error during ZIP creation for {video_id}. Error: {e}")
    #     return None
    # except Exception as e:
    #     logger.error(f"Service: An unexpected error occurred during ZIP creation for {video_id}. Error: {e}")
    #     return None

    # --- FAKE IMPLEMENTATION (CURRENTLY ACTIVE) ---
    logger.info(f"Service: Attempting to create ZIP for video_id: {video_id} using local dictionary.")
    song_doc = FAKE_ELASTICSEARCH_DB.get(video_id)
    if not song_doc or not _is_song_ready(song_doc):
        logger.error(f"Service: Cannot create ZIP for {video_id}. Song not found or not ready.")
        return None

    import tempfile
    import io

    # Create a temporary file for the ZIP
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

    with zipfile.ZipFile(temp_file.name, 'w') as zipf:
        zipf.writestr("vocals_removed.mp3", b"fake vocals removed audio")
        zipf.writestr("lyrics.lrc", b"[00:01.00]Fake lyrics")

    logger.info(f"Service: Successfully created ZIP file at {temp_file.name} for {video_id}.")
    return temp_file.name
