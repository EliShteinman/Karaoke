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

    def get_song_document(self, video_id: str) -> Optional[ElasticsearchSongDocument]:
        try:
            self.logger.debug(f"[{video_id}] - Calling repository to get song document.")
            song_data = self.song_repository.get_song(video_id)

            if not song_data:
                self.logger.warning(f"[{video_id}] - Repository returned no data for song.")
                return None
            
            self.logger.debug(f"[{video_id}] - Raw song data from repository: {song_data}")
            song_document = ElasticsearchSongDocument(**song_data)
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
            complex_update = {
                "status": "transcription_done",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "search_text": searchable_text
            }
            self.logger.debug(f"[{video_id}] - Performing final update with: {complex_update}")
            final_update_result = self.song_repository.es.update_document(video_id, complex_update)
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
            result = self.song_repository.mark_song_failed(
                video_id=video_id, error_code=error_details.code,
                error_message=error_details.message, service=error_details.service
            )
            if not result:
                self.logger.error(f"[{video_id}] - Repository failed to mark song as failed.")
            return result

        except Exception as e:
            self.logger.error(f"[{video_id}] - An exception occurred while updating song with error. Error: {e}")
            return False

    def _extract_searchable_text(self, lyrics_path: str, video_id: str) -> str:
        try:
            self.logger.debug(f"[{video_id}] - Extracting searchable text from: {lyrics_path}")
            lyrics_content = self.file_manager.read_file(lyrics_path)
            lines = [line.strip().split(']', 1)[-1] for line in lyrics_content.split('\n') if line.strip() and line.startswith('[') and ']' in line]
            searchable_text = " ".join(lines)
            self.logger.debug(f"[{video_id}] - Extracted {len(searchable_text)} characters of searchable text.")
            return searchable_text
        except Exception as e:
            self.logger.error(f"[{video_id}] - Could not extract searchable text from {lyrics_path}. Error: {e}")
            return ""
