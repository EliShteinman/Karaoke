import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from shared.elasticsearch.elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)


class SongRepository:
    """
    Repository for song documents in Elasticsearch
    Handles all song-specific operations for the HebKaraoke project
    """

    def __init__(self, es_service: ElasticsearchService):
        self.es = es_service

    async def create_song(
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
        Create a new song document with initial status 'downloading'
        """
        song_data = {
            "title": title,
            "artist": artist or "",
            "channel": channel or "",
            "duration": duration or 0,
            "thumbnail": thumbnail or "",
            "status": "downloading",
            "file_paths": {},
            "metadata": {},
            "search_text": search_text or f"{title} {artist} {channel}".strip(),
        }

        return await self.es.create_document(song_data, id=video_id)

    async def get_song(self, video_id: str) -> Optional[Dict]:
        """Get a song by video_id"""
        return await self.es.get_document(video_id)

    async def update_song_status(self, video_id: str, status: str) -> Optional[Dict]:
        """Update song status"""
        return await self.es.update_document(video_id, {"status": status})

    async def update_file_path(
        self, video_id: str, file_type: str, file_path: str
    ) -> Optional[Dict]:
        """
        Update file path for a specific file type
        file_type: 'original', 'vocals_removed', 'lyrics'
        """
        update_data = {f"file_paths.{file_type}": file_path}
        return await self.es.update_document(video_id, update_data)

    async def update_metadata(
        self, video_id: str, metadata: Dict
    ) -> Optional[Dict]:
        """Update song metadata"""
        update_data = {}
        for key, value in metadata.items():
            update_data[f"metadata.{key}"] = value
        return await self.es.update_document(video_id, update_data)

    async def mark_song_failed(
        self, video_id: str, error_code: str, error_message: str, service: str
    ) -> Optional[Dict]:
        """Mark song as failed with error details"""
        error_data = {
            "status": "failed",
            "error": {
                "code": error_code,
                "message": error_message,
                "timestamp": datetime.now(timezone.utc),
                "service": service,
            },
        }
        return await self.es.update_document(video_id, error_data)

    async def get_ready_songs(self) -> List[Dict]:
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
        async for hit in self.es.stream_all_documents(**search_params):
            results.append(hit["_source"])

        return results

    async def get_songs_by_status(self, status: str) -> List[Dict]:
        """Get songs by status"""
        search_params = {"term_filters": {"status": status}}

        results = []
        async for hit in self.es.stream_all_documents(**search_params):
            results.append(hit["_source"])

        return results

    async def search_songs(
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
        async for hit in self.es.stream_all_documents(**search_params):
            if count >= offset + limit:
                break
            if count >= offset:
                song = hit["_source"]
                song["video_id"] = hit["_id"]
                # Check if song is ready
                song["files_ready"] = self._is_song_ready(song)
                results.append(song)
            count += 1

        total_count = await self.es.count(**search_params)

        return {
            "songs": results,
            "total": total_count,
            "offset": offset,
            "limit": limit,
        }

    async def get_songs_for_processing(
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
        async for hit in self.es.stream_all_documents(**search_params):
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