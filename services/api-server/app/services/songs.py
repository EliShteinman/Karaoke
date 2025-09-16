from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import zipfile

# Corrected relative imports
from ..models import schemas
from ..core.config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

# --- FAKE DATABASE / ELASTICSEARCH DATA ---
# This dictionary simulates our Elasticsearch index.
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
            "original": f"{settings.SHARED_AUDIO_PATH}/dQw4w9WgXcQ/original.mp3",
            "vocals_removed": f"{settings.SHARED_AUDIO_PATH}/dQw4w9WgXcQ/vocals_removed.mp3",
            "lyrics": f"{settings.SHARED_AUDIO_PATH}/dQw4w9WgXcQ/lyrics.lrc"
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
            "original": f"{settings.SHARED_AUDIO_PATH}/oHg5SJYRHA0/original.mp3",
            # This song is not ready yet, missing vocals_removed and lyrics
        }
    }
}

# --- INTERNAL LOGIC (from _SCHEMAS.md) ---

def _is_song_ready(song_doc: Dict[str, Any]) -> bool:
    """Checks if a song is ready based on the architecture document."""
    file_paths = song_doc.get("file_paths", {})
    return bool(file_paths.get("vocals_removed") and file_paths.get("lyrics"))

def _calculate_progress(song_doc: Dict[str, Any]) -> schemas.Progress:
    """Calculates the progress of a song based on its document."""
    file_paths = song_doc.get("file_paths", {})
    return schemas.Progress(
        download=bool(file_paths.get("original")),
        audio_processing=bool(file_paths.get("vocals_removed")),
        transcription=bool(file_paths.get("lyrics")),
        files_ready=_is_song_ready(song_doc)
    )

# --- SERVICE FUNCTIONS (to be called by routers) ---

async def get_all_songs() -> schemas.SongsResponse:
    """(Fake) Fetches all songs and returns them in the correct format."""
    logger.info("Service: Fetching all songs from the fake database.")
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
    """(Fake) Fetches the status of a specific song."""
    logger.info(f"Service: Fetching status for video_id: {video_id}")
    song_doc = FAKE_ELASTICSEARCH_DB.get(video_id)

    if not song_doc:
        logger.warning(f"Service: Song with video_id: {video_id} not found in fake DB.")
        return None

    progress = _calculate_progress(song_doc)
    status_response = schemas.StatusResponse(
        video_id=song_doc["video_id"],
        status=song_doc["status"],
        progress=progress
    )
    logger.info(f"Service: Status for {video_id} is {status_response.dict()}")
    return status_response

async def create_song_zip_file(video_id: str) -> Optional[str]:
    """(Fake) Creates a ZIP file with the song's assets."""
    logger.info(f"Service: Attempting to create ZIP for video_id: {video_id}")
    song_doc = FAKE_ELASTICSEARCH_DB.get(video_id)

    if not song_doc or not _is_song_ready(song_doc):
        logger.error(f"Service: Cannot create ZIP for {video_id}. Song not found or not ready.")
        return None

    # TODO: When working with real files, validate they exist before creating ZIP
    # file_paths = song_doc.get("file_paths", {})
    # required_files = ["vocals_removed", "lyrics"]
    # for file_type in required_files:
    #     file_path = file_paths.get(file_type)
    #     if not file_path or not os.path.exists(file_path):
    #         logger.error(f"Service: Required file {file_type} not found at {file_path}")
    #         return None

    # This part is purely for demonstration so the zipfile has content.
    # In a real app, you would use the actual file paths from the song_doc.
    temp_dir = f"/tmp/{video_id}"
    os.makedirs(temp_dir, exist_ok=True)
    fake_vocals_path = os.path.join(temp_dir, "vocals_removed.mp3")
    fake_lyrics_path = os.path.join(temp_dir, "lyrics.lrc")
    with open(fake_vocals_path, "w") as f:
        f.write("fake vocals removed audio")
    with open(fake_lyrics_path, "w") as f:
        f.write("[00:01.00]Fake lyrics")

    zip_path = f"/tmp/{video_id}.zip"
    logger.info(f"Service: Creating zip file at: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(fake_vocals_path, arcname="vocals_removed.mp3")
        zipf.write(fake_lyrics_path, arcname="lyrics.lrc")
    
    logger.info(f"Service: Successfully created ZIP file for {video_id}.")
    return zip_path
