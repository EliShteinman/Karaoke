import logging
from datetime import datetime, timezone
from typing import Dict, Generator, List, Optional

from ..elasticsearch.elasticsearch_service_sync import ElasticsearchServiceSync

logger = logging.getLogger(__name__)


class SongRepositorySync:
    """
    Synchronous repository for song documents in Elasticsearch
    Handles all song-specific operations for the HebKaraoke project
    """

    def __init__(self, es_service: ElasticsearchServiceSync):
        self.es = es_service

    def create_song(
        self,
        video_id: str,
        title: str,
        artist: str = None,
        channel: str = None,
        duration: int = None,
        thumbnail: str = None,
        search_text: str = None,
    ) -> Dict:
        """
        Create a new song document with initial detailed status structure
        """
        song_data = {
            "title": title,
            "artist": artist or "",
            "channel": channel or "",
            "duration": duration or 0,
            "thumbnail": thumbnail or "",
            "status": {
                "overall": "downloading",
                "download": "pending",
                "audio_processing": "pending",
                "transcription": "pending"
            },
            "file_paths": {},
            "metadata": {},
            "search_text": search_text or f"{title} {artist} {channel}".strip(),
        }

        return self.es.create_document(song_data, id=video_id)

    def get_song(self, video_id: str) -> Optional[Dict]:
        """Get a song by video_id"""
        return self.es.get_document(video_id)

    def update_song_status(self, video_id: str, status: str) -> Optional[Dict]:
        """Update song status (legacy method for backward compatibility)"""
        return self.es.update_document(video_id, {"status": status})

    def update_status_field(self, video_id: str, field: str, value: str) -> Optional[Dict]:
        """
        Update a specific status field in the detailed status structure

        Args:
            video_id: The song video ID
            field: Status field ('overall', 'download', 'audio_processing', 'transcription')
            value: Status value ('pending', 'in_progress', 'completed', 'failed')
        """
        update_data = {f"status.{field}": value}
        return self.es.update_document(video_id, update_data)

    def update_status_and_check_completion(self, video_id: str, field: str, value: str) -> Optional[Dict]:
        """
        Update a specific status field and automatically set overall to 'completed' if all steps are done

        This method is intelligent - when a processing step is marked as 'completed',
        it checks if ALL processing steps are completed and automatically updates the overall status.

        Args:
            video_id: The song video ID
            field: Status field ('download', 'audio_processing', 'transcription')
            value: Status value ('pending', 'in_progress', 'completed', 'failed')
        """
        # First update the specific field
        result = self.update_status_field(video_id, field, value)

        # If this was a completion and result successful, check if all are complete
        if result and value == "completed":
            # Fetch current document to check all statuses
            current_doc = self.get_song(video_id)
            if current_doc:
                status = current_doc.get("status", {})
                if (status.get("download") == "completed" and
                    status.get("audio_processing") == "completed" and
                    status.get("transcription") == "completed"):
                    # All complete - update overall status
                    logger.info(f"All processing steps completed for {video_id}, setting overall status to 'completed'")
                    return self.update_status_field(video_id, "overall", "completed")

        # If this was a failure, set overall status to failed as well
        elif result and value == "failed":
            logger.warning(f"Step {field} failed for {video_id}, setting overall status to 'failed'")
            return self.update_status_field(video_id, "overall", "failed")

        return result

    def update_file_path(
        self, video_id: str, file_type: str, file_path: str
    ) -> Optional[Dict]:
        """
        Update file path for a specific file type
        file_type: 'original', 'vocals_removed', 'lyrics'
        """
        update_data = {f"file_paths.{file_type}": file_path}
        return self.es.update_document(video_id, update_data)

    def update_metadata(
        self, video_id: str, metadata: Dict
    ) -> Optional[Dict]:
        """Update song metadata"""
        update_data = {}
        for key, value in metadata.items():
            update_data[f"metadata.{key}"] = value
        return self.es.update_document(video_id, update_data)

    def mark_song_failed(
        self, video_id: str, error_code: str, error_message: str, service: str,
        failed_step: str = None
    ) -> Optional[Dict]:
        """
        Mark song as failed with error details

        Args:
            video_id: The song video ID
            error_code: Error code
            error_message: Error message
            service: Service that reported the failure
            failed_step: Specific step that failed ('download', 'audio_processing', 'transcription')
        """
        error_data = {
            "error": {
                "code": error_code,
                "message": error_message,
                "timestamp": datetime.now(timezone.utc),
                "service": service,
            },
        }

        # Update the appropriate status fields
        if failed_step:
            error_data[f"status.{failed_step}"] = "failed"
        error_data["status.overall"] = "failed"

        return self.es.update_document(video_id, error_data)

    def get_ready_songs(self) -> List[Dict]:
        """
        Get all songs that are ready for karaoke
        (have both vocals_removed and lyrics files)
        """
        search_params = {
            "exists_filters": ["file_paths.vocals_removed", "file_paths.lyrics"],
            "script_filters": [
                "doc['file_paths.vocals_removed'].size() > 0",
                "doc['file_paths.lyrics'].size() > 0",
                "!doc['file_paths.vocals_removed'].value.empty",
                "!doc['file_paths.lyrics'].value.empty",
            ],
        }

        results = []
        for hit in self.es.stream_all_documents(**search_params):
            song = hit["_source"]
            song["video_id"] = hit["_id"]
            results.append(song)

        return results

    def get_songs_by_status(self, status: str) -> List[Dict]:
        """Get songs by status"""
        search_params = {"term_filters": {"status": status}}

        results = []
        for hit in self.es.stream_all_documents(**search_params):
            song = hit["_source"]
            song["video_id"] = hit["_id"]
            results.append(song)

        return results

    def search_songs(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> Dict:
        """
        Search songs by text query
        Returns both ready and non-ready songs
        """
        # This is a simplified search - in production you'd want more sophisticated search
        search_params = {"query_text": query}

        results = []
        count = 0
        for hit in self.es.stream_all_documents(**search_params):
            if count >= offset + limit:
                break
            if count >= offset:
                song = hit["_source"]
                song["video_id"] = hit["_id"]
                # Check if song is ready
                song["files_ready"] = self._is_song_ready(song)
                results.append(song)
            count += 1

        total_count = self.es.count(**search_params)

        return {
            "songs": results,
            "total": total_count,
            "offset": offset,
            "limit": limit,
        }

    def get_songs_for_processing(
        self, file_type: str, status: str = "downloaded"
    ) -> List[Dict]:
        """
        Get songs that need processing for a specific file type
        file_type: 'vocals_removed' or 'lyrics'
        """
        search_params = {
            "term_filters": {"status": status},
            "not_exists_filters": [f"file_paths.{file_type}"],
        }

        results = []
        for hit in self.es.stream_all_documents(**search_params):
            song = hit["_source"]
            song["video_id"] = hit["_id"]
            results.append(song)

        return results

    def _is_song_ready(self, song: Dict) -> bool:
        """Check if song has both required files for karaoke"""
        file_paths = song.get("file_paths", {})
        vocals_removed = file_paths.get("vocals_removed")
        lyrics = file_paths.get("lyrics")

        return bool(
            vocals_removed
            and lyrics
            and vocals_removed.strip()
            and lyrics.strip()
        )