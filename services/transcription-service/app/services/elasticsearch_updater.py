from datetime import datetime
from elasticsearch import Elasticsearch, NotFoundError
import os

class ElasticsearchUpdater:
    def __init__(self):
        self.client = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_HOST")])

    def get_song_document(self, video_id: str):
        try:
            response = self.client.get(index="songs", id=video_id)
            return response.get("_source")
        except NotFoundError:
            # It's better to return None and let the caller handle the "not found" case
            return None

    def update_song_document(self, video_id: str, lyrics_path: str, processing_metadata: dict):
        doc_update = {
            "file_paths.lyrics": lyrics_path,
            "updated_at": datetime.utcnow().isoformat(),
            "status": "transcription_done", # Explicitly update status
            "processing_metadata.transcription": processing_metadata,
            "search_text": self._extract_searchable_text(lyrics_path)
        }
        self.client.update(index="songs", id=video_id, body={"doc": doc_update})

    def update_song_with_error(self, video_id: str, error_details: dict):
        error_payload = {
            "status": "failed",
            "error": error_details,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.client.update(index="songs", id=video_id, body={"doc": error_payload})


    def _extract_searchable_text(self, lyrics_path: str) -> str:
        try:
            with open(lyrics_path, 'r', encoding="utf-8") as f:
                # We remove timestamps and metadata for a cleaner search text
                lines = [line for line in f if not line.startswith('[')]
                return " ".join(lines).replace("\n", " ")
        except FileNotFoundError:
            return ""
