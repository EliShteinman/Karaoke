"""
Elasticsearch updater service using shared repository patterns
Handles all Elasticsearch operations for the transcription service
"""
from datetime import datetime, timezone
from typing import Optional

from shared.repositories.factory import RepositoryFactory
from shared.repositories.song_repository_sync import SongRepositorySync
from shared.storage.file_storage import create_file_manager
from shared.utils.logger import Logger
from shared.utils.data_utils import normalize_elasticsearch_song_document

# Import config and models
from services.transcriptionService.app.services.config import TranscriptionServiceConfig
from services.transcriptionService.app.models import (
    ElasticsearchSongDocument,
    ProcessingMetadata,
    ErrorDetails
)


class ElasticsearchUpdater:
    """
    Service for updating Elasticsearch documents
    Uses shared repository pattern for consistency across services
    """

    def __init__(self) -> None:
        self.logger = Logger.get_logger(__name__)
        self.config = TranscriptionServiceConfig()

        try:
            self.song_repository: SongRepositorySync = RepositoryFactory.create_song_repository_from_params(
                elasticsearch_host=self.config.elasticsearch_host,
                elasticsearch_port=self.config.elasticsearch_port,
                elasticsearch_scheme=self.config.elasticsearch_scheme,
                songs_index=self.config.elasticsearch_songs_index,
                async_mode=False
            )
            self.file_manager = create_file_manager(
                storage_type="volume",
                base_path=self.config.storage_base_path
            )
            self.logger.info("ElasticsearchUpdater initialized successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize ElasticsearchUpdater. Error: {e}")
            raise

    def update_status_field(self, video_id: str, field: str, value: str) -> bool:
        """
        Update a specific status field using the shared repository

        Args:
            video_id: YouTube video ID
            field: Status field ('transcription', 'audio_processing', 'download', 'overall')
            value: Status value ('pending', 'in_progress', 'completed', 'failed')

        Returns:
            True if update was successful, False otherwise
        """
        try:
            self.logger.debug(f"[{video_id}] - Updating status field '{field}' to '{value}'")
            result = self.song_repository.update_status_field(video_id, field, value)

            if result:
                self.logger.debug(f"[{video_id}] - Successfully updated status field '{field}' to '{value}'")
                return True
            else:
                self.logger.error(f"[{video_id}] - Failed to update status field '{field}' to '{value}'")
                return False

        except Exception as e:
            self.logger.error(f"[{video_id}] - Exception updating status field '{field}': {e}")
            return False

    def get_song_document(self, video_id: str) -> Optional[ElasticsearchSongDocument]:
        try:
            self.logger.debug(f"[{video_id}] - Calling repository to get song document.")
            song_data = self.song_repository.get_song(video_id)

            if not song_data:
                self.logger.warning(f"[{video_id}] - Repository returned no data for song.")
                return None

            self.logger.debug(f"[{video_id}] - Raw song data from repository: {song_data}")

            # Convert flat structure to nested structure for our model
            normalized_data = normalize_elasticsearch_song_document(song_data)
            self.logger.debug(f"[{video_id}] - Normalized song data: {normalized_data}")

            song_document = ElasticsearchSongDocument(**normalized_data)
            return song_document

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to get and parse song document. Error: {e}")
            return None


    def update_song_document(self, video_id: str, lyrics_path: str, processing_metadata: ProcessingMetadata) -> bool:
        try:
            self.logger.debug(f"[{video_id}] - Updating lyrics file path to: {lyrics_path}")
            file_update_result = self.song_repository.update_file_path(video_id=video_id, file_type="lyrics", file_path=lyrics_path)
            if not file_update_result:
                self.logger.error(f"[{video_id}] - Failed to update lyrics file path in repository.")
                return False

            metadata_dict = {"transcription": processing_metadata.dict()}
            self.logger.debug(f"[{video_id}] - Updating processing metadata with: {metadata_dict}")
            metadata_update_result = self.song_repository.update_metadata(video_id=video_id, metadata=metadata_dict)
            if not metadata_update_result:
                self.logger.error(f"[{video_id}] - Failed to update metadata in repository.")
                return False

            searchable_text = self._extract_searchable_text(lyrics_path, video_id)

            # Update searchable text first
            search_text_update = {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "search_text": searchable_text
            }
            text_update_result = self.song_repository.es.update_document(video_id, search_text_update)

            if not text_update_result:
                self.logger.error(f"[{video_id}] - Failed to update search text")
                return False

            # Use intelligent status completion check - this will automatically set overall to 'completed' if all steps are done
            final_update_result = self.song_repository.update_status_and_check_completion(
                video_id, "transcription", "completed"
            )
            if not final_update_result:
                self.logger.error(f"[{video_id}] - Failed to perform final update in repository.")
                return False

            self.logger.info(f"[{video_id}] - Successfully updated document with all transcription results.")
            return True

        except Exception as e:
            self.logger.error(f"[{video_id}] - An exception occurred while updating song document. Error: {e}")
            return False

    def update_song_with_error(self, video_id: str, error_details: ErrorDetails) -> bool:
        try:
            self.logger.warning(f"[{video_id}] - Updating document with error details: {error_details.dict()}")

            # Use shared repository to mark song as failed - specify transcription step failed
            result = self.song_repository.mark_song_failed(
                video_id=video_id,
                error_code=error_details.code,
                error_message=error_details.message,
                service=error_details.service,
                failed_step="transcription"
            )
            if not result:
                self.logger.error(f"[{video_id}] - Repository failed to mark song as failed.")
            return result

        except Exception as e:
            self.logger.error(f"[{video_id}] - An exception occurred while updating song with error. Error: {e}")
            return False

    def _extract_searchable_text(self, lyrics_path: str, video_id: str) -> str:
        """
        Extract searchable text from LRC file using proper file manager

        Args:
            lyrics_path: Path to the LRC file
            video_id: Video ID for logging

        Returns:
            str: Extracted text content for search indexing
        """
        try:
            self.logger.debug(f"[{video_id}] - Extracting searchable text from: {lyrics_path}")

            # Convert absolute path to relative path that file manager expects
            if lyrics_path.startswith('data/audio/'):
                relative_path = lyrics_path[len('data/audio/'):]
            else:
                relative_path = lyrics_path

            # Verify file exists before reading
            if not self.file_manager.storage.file_exists(relative_path):
                self.logger.warning(f"[{video_id}] - LRC file not found at: {lyrics_path}")
                return ""

            # Use proper file manager method to read file content
            lyrics_content = self.file_manager.storage.read_text_file(relative_path)

            if not lyrics_content:
                self.logger.warning(f"[{video_id}] - LRC file is empty: {lyrics_path}")
                return ""

            # Extract only the text content from LRC timestamps [mm:ss.ss]text
            lines = []
            for line in lyrics_content.split('\n'):
                line = line.strip()
                if line and line.startswith('[') and ']' in line:
                    # Skip metadata lines like [ar:artist] but include timed lyrics [00:12.34]text
                    if ':' in line and not line.startswith('[ar:') and not line.startswith('[ti:') and not line.startswith('[al:') and not line.startswith('[by:'):
                        text_part = line.split(']', 1)[-1].strip()
                        if text_part:
                            lines.append(text_part)

            searchable_text = " ".join(lines)
            self.logger.debug(f"[{video_id}] - Extracted {len(searchable_text)} characters of searchable text from {len(lines)} lyrics lines.")
            return searchable_text

        except Exception as e:
            self.logger.error(f"[{video_id}] - Could not extract searchable text from {lyrics_path}. Error: {e}")
            return ""
