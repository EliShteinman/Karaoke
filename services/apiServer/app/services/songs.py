from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import zipfile
import json
import io
from shared.repositories.factory import RepositoryFactory
from shared.storage.file_storage import create_file_manager
from shared.utils.data_utils import normalize_elasticsearch_song_document
from services.apiServer.app.models import schemas
from services.apiServer.app.config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)


# --- INTERNAL LOGIC ---
def _is_song_ready(song_doc: Dict[str, Any]) -> bool:
    """Check if song has both required files for karaoke."""
    file_paths = song_doc.get("file_paths", {})

    # Check for files in both the nested object and as separate fields (for backward compatibility)
    vocals_removed = file_paths.get("vocals_removed") or song_doc.get("file_paths.vocals_removed")
    lyrics = file_paths.get("lyrics") or song_doc.get("file_paths.lyrics")

    return bool(
        vocals_removed and lyrics and
        str(vocals_removed).strip() and str(lyrics).strip()
    )

def _calculate_is_ready(song_doc: Dict[str, Any]) -> bool:
    """Calculate if song is ready based on the new detailed status structure."""
    status = song_doc.get("status", {})

    # Handle both new detailed status structure and legacy status field
    if isinstance(status, dict):
        # New detailed status structure
        return (
            status.get("download") == "completed" and
            status.get("audio_processing") == "completed" and
            status.get("transcription") == "completed" and
            status.get("overall") == "completed"
        )
    else:
        # Legacy status - fall back to file-based check
        return _is_song_ready(song_doc)

def _extract_status_details(song_doc: Dict[str, Any]) -> schemas.StatusDetails:
    """Extract detailed status information from song document."""
    status = song_doc.get("status", {})

    # Handle both new detailed status structure and legacy status field
    if isinstance(status, dict):
        # New detailed status structure
        return schemas.StatusDetails(
            overall=status.get("overall", "unknown"),
            download=status.get("download", "unknown"),
            audio_processing=status.get("audio_processing", "unknown"),
            transcription=status.get("transcription", "unknown")
        )
    else:
        # Legacy status - convert to detailed structure based on files
        progress = _calculate_progress(song_doc)
        return schemas.StatusDetails(
            overall=str(status) if status else "unknown",
            download="completed" if progress.download else "pending",
            audio_processing="completed" if progress.audio_processing else "pending",
            transcription="completed" if progress.transcription else "pending"
        )

def _calculate_progress(song_doc: Dict[str, Any]) -> schemas.Progress:
    """Calculate processing progress for a song based on file paths (legacy for backward compatibility)."""
    file_paths = song_doc.get("file_paths", {})

    # Check for files in both the nested object and as separate fields (for backward compatibility)
    has_original = bool(file_paths.get("original") or song_doc.get("file_paths.original"))
    has_vocals = bool(file_paths.get("vocals_removed") or song_doc.get("file_paths.vocals_removed"))
    has_lyrics = bool(file_paths.get("lyrics") or song_doc.get("file_paths.lyrics"))

    return schemas.Progress(
        download=has_original,
        audio_processing=has_vocals,
        transcription=has_lyrics,
        files_ready=_is_song_ready(song_doc)
    )

# --- SERVICE FUNCTIONS ---

async def get_all_songs() -> schemas.SongsResponse:
    """
    Fetches all songs from the data source with progress information.

    Returns:
        schemas.SongsResponse: Response containing all songs (ready, processing, failed) with progress
    """
    song_repo = None
    try:
        logger.info("Service: Getting song repository from factory.")
        song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True)
        logger.info("Service: Fetching all songs from repository (ready, processing, failed).")
        all_songs_docs = await song_repo.get_all_songs()

        song_list: List[schemas.SongListItem] = []
        for doc in all_songs_docs:
            try:
                # Normalize document structure for consistent access
                normalized_doc = normalize_elasticsearch_song_document(doc)

                # Calculate progress for each song
                progress = _calculate_progress(normalized_doc)

                # Extract status - handle both detailed status object and legacy string status
                status_data = doc.get("status", {})
                if isinstance(status_data, dict):
                    status_string = status_data.get("overall", "unknown")
                else:
                    status_string = str(status_data) if status_data else "unknown"

                song_item = schemas.SongListItem(
                    video_id=doc.get("video_id", ""),
                    title=doc.get("title", ""),
                    artist=doc.get("artist", ""),
                    status=status_string,
                    created_at=doc.get("created_at"),
                    thumbnail=doc.get("thumbnail", ""),
                    duration=doc.get("duration", 0),
                    progress=progress,
                    files_ready=progress.files_ready  # Use calculated progress for consistency
                )
                song_list.append(song_item)
            except (KeyError, ValueError, TypeError) as song_error:
                logger.error(f"Service: Failed to process song document {doc.get('video_id', 'unknown')}: {song_error}")
                continue
            except Exception as song_error:
                logger.error(f"Service: Unexpected error processing song document {doc.get('video_id', 'unknown')}: {song_error}")
                continue

        logger.info(f"Service: Found {len(song_list)} songs total (all statuses).")
        return schemas.SongsResponse(songs=song_list)
    except ConnectionError as e:
        logger.error(f"Service: Failed to connect to Elasticsearch while getting all songs. Error: {e}")
        raise
    except TimeoutError as e:
        logger.error(f"Service: Timeout while getting all songs from Elasticsearch. Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred while getting all songs. Error: {e}")
        raise

async def get_song_status(video_id: str) -> Optional[schemas.StatusResponse]:
    """Fetches the status of a specific song from the data source."""
    song_repo = None
    try:
        logger.info(f"Service: Getting song repository to fetch status for video_id: {video_id}.")
        song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True)
        song_doc = await song_repo.get_song(video_id)

        if not song_doc:
            logger.warning(f"Service: Song with video_id: {video_id} not found in repository.")
            return None

        logger.info(f"Service: Found document for video_id: {video_id}.")

        # Normalize document structure for consistent access
        normalized_doc = normalize_elasticsearch_song_document(song_doc)

        # Extract detailed status and calculate readiness
        status_details = _extract_status_details(normalized_doc)
        is_ready = _calculate_is_ready(normalized_doc)
        progress = _calculate_progress(normalized_doc)  # Keep for backward compatibility

        return schemas.StatusResponse(
            video_id=song_doc["video_id"],
            status=status_details,
            is_ready=is_ready,
            progress=progress
        )
    except KeyError as e:
        logger.error(f"Service: Missing required field in song document for video_id: {video_id}. Error: {e}")
        return None
    except ConnectionError as e:
        logger.error(f"Service: Failed to connect to Elasticsearch for video_id: {video_id}. Error: {e}")
        raise
    except TimeoutError as e:
        logger.error(f"Service: Timeout while fetching song status for video_id: {video_id}. Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred for video_id: {video_id}. Error: {e}")
        raise

async def create_song_zip_file(video_id: str) -> Optional[bytes]:
    """Creates an in-memory ZIP package with vocals_removed.wav and lyrics.json."""
    try:
        logger.info(f"Service: Creating ZIP package with JSON lyrics for video_id: {video_id}.")

        # Get song document from Elasticsearch
        song_repo = RepositoryFactory.create_song_repository_from_config(settings, async_mode=True)
        song_doc = await song_repo.get_song(video_id)

        if not song_doc:
            logger.error(f"Service: Song document not found for {video_id}.")
            return None

        # Normalize document structure for consistent access
        normalized_doc = normalize_elasticsearch_song_document(song_doc)

        # Extract file paths
        file_paths = normalized_doc.get("file_paths", {})
        vocals_removed_path = file_paths.get("vocals_removed")

        if not vocals_removed_path:
            logger.error(f"Service: No vocals_removed file path found for {video_id}.")
            return None

        # Get audio file content
        file_manager = create_file_manager(
            storage_type="volume",
            base_path=settings.shared_storage_base_path
        )

        try:
            vocals_content = file_manager.storage.read_file(vocals_removed_path)
        except Exception as e:
            logger.error(f"Service: Failed to read vocals_removed file for {video_id}. Error: {e}")
            return None

        # Extract transcription segments and flatten to word list
        metadata = normalized_doc.get("metadata", {})
        transcription = metadata.get("transcription", {})
        segments = transcription.get("segments", [])

        if not segments:
            logger.error(f"Service: No transcription segments found for {video_id}.")
            return None

        # Flatten all words from all segments into a single list
        word_list = []
        for segment in segments:
            if isinstance(segment, dict) and "words" in segment and segment["words"]:
                for word in segment["words"]:
                    if isinstance(word, dict) and all(key in word for key in ["word", "start", "end", "probability"]):
                        word_list.append({
                            "word": word["word"],
                            "start": word["start"],
                            "end": word["end"],
                            "probability": word["probability"]
                        })

        if not word_list:
            logger.error(f"Service: No word-level timing data found for {video_id}.")
            return None

        # Convert word list to JSON string
        lyrics_json = json.dumps(word_list, ensure_ascii=False, indent=2)

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("vocals_removed.wav", vocals_content)
            zip_file.writestr("lyrics.json", lyrics_json.encode("utf-8"))

        zip_content = zip_buffer.getvalue()
        logger.info(f"Service: Successfully created JSON karaoke package for {video_id} ({len(zip_content)} bytes, {len(word_list)} words).")
        return zip_content

    except Exception as e:
        logger.error(f"Service: An unexpected error occurred during ZIP creation for {video_id}. Error: {e}")
        return None
