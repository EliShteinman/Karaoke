from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import zipfile
from shared.repositories.factory import RepositoryFactory
from shared.storage.file_storage import create_file_manager
from services.apiServer.app.models import schemas
from services.apiServer.app.config import settings
from shared.utils.logger import Logger

logger = Logger.get_logger(name="api-server-services")


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

def _calculate_progress(song_doc: Dict[str, Any]) -> schemas.Progress:
    """Calculate processing progress for a song based on file paths."""
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
                # Calculate progress for each song
                progress = _calculate_progress(doc)

                song_item = schemas.SongListItem(
                    video_id=doc.get("video_id", ""),
                    title=doc.get("title", ""),
                    artist=doc.get("artist", ""),
                    status=doc.get("status", ""),
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
        progress = _calculate_progress(song_doc)

        return schemas.StatusResponse(
            video_id=song_doc["video_id"],
            status=song_doc["status"],
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
    """Creates an in-memory ZIP package with the song's assets."""
    try:
        logger.info(f"Service: Creating file manager for ZIP creation for video_id: {video_id}.")

        # Use centralized storage configuration
        file_manager = create_file_manager(
            storage_type="volume",
            base_path=settings.shared_storage_base_path
        )

        # Check song readiness before attempting to create package
        if not file_manager.is_song_ready_for_karaoke(video_id):
            logger.error(f"Service: Cannot create ZIP for {video_id}. Song is not ready.")
            return None

        logger.info(f"Service: Song {video_id} is ready. Creating in-memory ZIP package.")
        zip_content = file_manager.create_karaoke_package(video_id)
        logger.info(f"Service: Successfully created ZIP package for {video_id} ({len(zip_content)} bytes).")
        return zip_content

    except ValueError as e:
        logger.error(f"Service: Value error during ZIP creation for {video_id}. Error: {e}")
        return None
    except FileNotFoundError as e:
        logger.error(f"Service: Required files not found for {video_id}. Error: {e}")
        return None
    except PermissionError as e:
        logger.error(f"Service: Permission denied accessing files for {video_id}. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Service: An unexpected error occurred during ZIP creation for {video_id}. Error: {e}")
        return None
