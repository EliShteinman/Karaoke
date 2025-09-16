"""
Elasticsearch updater service using shared repository patterns
Handles all Elasticsearch operations for the transcription service
"""
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from shared.repositories.factory import RepositoryFactory
from shared.repositories.song_repository_sync import SongRepositorySync
from shared.storage import create_file_manager
from shared.utils.logger import Logger

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

        # Initialize shared repository
        try:
            self.song_repository: SongRepositorySync = RepositoryFactory.create_song_repository_from_params(
                elasticsearch_host=os.getenv("ELASTICSEARCH_HOST", "localhost"),
                elasticsearch_port=int(os.getenv("ELASTICSEARCH_PORT", "9200")),
                elasticsearch_scheme=os.getenv("ELASTICSEARCH_SCHEME", "http"),
                elasticsearch_username=os.getenv("ELASTICSEARCH_USERNAME"),
                elasticsearch_password=os.getenv("ELASTICSEARCH_PASSWORD"),
                songs_index=os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs"),
                async_mode=False
            )

            # Initialize file manager for reading lyrics content
            self.file_manager = create_file_manager(
                storage_type="volume",
                base_path=os.getenv("SHARED_STORAGE_PATH", "/shared")
            )

            self.logger.info("ElasticsearchUpdater initialized successfully with shared repository")

        except Exception as e:
            self.logger.critical(f"Failed to initialize ElasticsearchUpdater. Error: {e}")
            self.logger.error(f"ElasticsearchUpdater initialization error details: {str(e)}")
            raise

    def get_song_document(self, video_id: str) -> Optional[ElasticsearchSongDocument]:
        """
        Get song document from Elasticsearch using shared repository

        Args:
            video_id: YouTube video ID

        Returns:
            Song document or None if not found
        """
        try:
            self.logger.debug(f"[{video_id}] - Getting document from Elasticsearch")
            song_data = self.song_repository.get_song(video_id)

            if not song_data:
                self.logger.warning(f"[{video_id}] - Document not found in Elasticsearch")
                return None

            # Validate and structure the document
            song_document = ElasticsearchSongDocument(
                video_id=video_id,
                title=song_data.get("title", ""),
                artist=song_data.get("artist", ""),
                album=song_data.get("album", ""),
                file_paths=song_data.get("file_paths", {}),
                status=song_data.get("status", "unknown")
            )

            self.logger.debug(f"[{video_id}] - Successfully retrieved song document")
            return song_document

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to get document from Elasticsearch. Error: {e}")
            self.logger.error(f"[{video_id}] - Get document error details: {str(e)}")
            return None

    def update_song_document(
        self,
        video_id: str,
        lyrics_path: str,
        processing_metadata: ProcessingMetadata
    ) -> bool:
        """
        Update song document with transcription results

        Args:
            video_id: YouTube video ID
            lyrics_path: Path to the LRC lyrics file
            processing_metadata: Processing metadata from transcription

        Returns:
            True if update was successful, False otherwise
        """
        try:
            self.logger.debug(f"[{video_id}] - Updating document with transcription results")

            # Update file path for lyrics
            file_update_result = self.song_repository.update_file_path(
                video_id=video_id,
                file_type="lyrics",
                file_path=lyrics_path
            )

            if not file_update_result:
                self.logger.error(f"[{video_id}] - Failed to update lyrics file path")
                return False

            # Update processing metadata
            metadata_dict = {
                "transcription": {
                    "processing_time": processing_metadata.processing_time,
                    "confidence_score": processing_metadata.confidence_score,
                    "language_detected": processing_metadata.language_detected,
                    "language_probability": processing_metadata.language_probability,
                    "word_count": processing_metadata.word_count,
                    "line_count": processing_metadata.line_count,
                    "model_used": processing_metadata.model_used,
                    "duration_seconds": processing_metadata.duration_seconds
                }
            }

            metadata_update_result = self.song_repository.update_metadata(
                video_id=video_id,
                metadata=metadata_dict
            )

            if not metadata_update_result:
                self.logger.error(f"[{video_id}] - Failed to update processing metadata")
                return False

            # Extract searchable text from lyrics file
            searchable_text = self._extract_searchable_text(lyrics_path, video_id)

            # Update searchable text and status - using the elasticsearch service directly for complex updates
            complex_update = {
                "status": "transcription_done",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "search_text": searchable_text
            }

            final_update_result = self.song_repository.es.update_document(video_id, complex_update)

            if not final_update_result:
                self.logger.error(f"[{video_id}] - Failed to update status and search text")
                return False

            self.logger.info(f"[{video_id}] - Successfully updated document with transcription results")
            return True

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to update document in Elasticsearch. Error: {e}")
            self.logger.error(f"[{video_id}] - Update document error details: {str(e)}")
            return False

    def update_song_with_error(self, video_id: str, error_details: ErrorDetails) -> bool:
        """
        Update song document with error information

        Args:
            video_id: YouTube video ID
            error_details: Error details to store

        Returns:
            True if update was successful, False otherwise
        """
        try:
            self.logger.debug(f"[{video_id}] - Updating document with error details")

            # Use shared repository to mark song as failed
            result = self.song_repository.mark_song_failed(
                video_id=video_id,
                error_code=error_details.code,
                error_message=error_details.message,
                service=error_details.service
            )

            if result:
                self.logger.info(f"[{video_id}] - Successfully updated document with error details")
                return True
            else:
                self.logger.error(f"[{video_id}] - Failed to update document with error details")
                return False

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to update document with error details. Error: {e}")
            self.logger.error(f"[{video_id}] - Update error details error: {str(e)}")
            return False

    def _extract_searchable_text(self, lyrics_path: str, video_id: str) -> str:
        """
        Extract searchable text from lyrics file using shared file storage

        Args:
            lyrics_path: Path to the LRC lyrics file
            video_id: YouTube video ID for logging

        Returns:
            Extracted searchable text
        """
        try:
            # Use shared file manager to read lyrics content
            lyrics_content = self.file_manager.get_lyrics(video_id)

            # Extract text lines (remove LRC timestamp markers)
            lines = []
            for line in lyrics_content.split('\n'):
                line = line.strip()
                # Skip metadata lines and empty lines
                if line and not line.startswith('[ar:') and not line.startswith('[ti:') and not line.startswith('[al:') and not line.startswith('[by:'):
                    # Remove timestamp from lyrics lines [mm:ss.xx]
                    if line.startswith('[') and ']' in line:
                        text_part = line.split(']', 1)[1] if ']' in line else line
                        if text_part.strip():
                            lines.append(text_part.strip())
                    elif not line.startswith('['):
                        lines.append(line)

            searchable_text = " ".join(lines)
            self.logger.debug(f"[{video_id}] - Extracted searchable text: {len(searchable_text)} characters")
            return searchable_text

        except Exception as e:
            self.logger.error(f"[{video_id}] - Could not extract searchable text from lyrics. Error: {e}")
            self.logger.error(f"[{video_id}] - Extract searchable text error details: {str(e)}")
            return ""