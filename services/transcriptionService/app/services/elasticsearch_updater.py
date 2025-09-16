from datetime import datetime
from elasticsearch import Elasticsearch, NotFoundError
import os
from shared.utils.logger import Logger

class ElasticsearchUpdater:
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.client = None
        try:
            self.client = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_HOST")])
            # Verify connection
            if not self.client.ping():
                raise ConnectionError("Elasticsearch ping failed.")
            self.logger.info("Successfully connected to Elasticsearch.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize Elasticsearch client. Error: {e}")
            raise

    def get_song_document(self, video_id: str):
        if not self.client:
            return None
        try:
            self.logger.debug(f"[{video_id}] - Getting document from Elasticsearch.")
            response = self.client.get(index="songs", id=video_id)
            return response.get("_source")
        except NotFoundError:
            self.logger.warning(f"[{video_id}] - Document not found in Elasticsearch.")
            return None
        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to get document from Elasticsearch. Error: {e}")
            return None

    def update_song_document(self, video_id: str, lyrics_path: str, processing_metadata: dict):
        if not self.client:
            return
        try:
            doc_update = {
                "file_paths.lyrics": lyrics_path,
                "updated_at": datetime.utcnow().isoformat(),
                "status": "transcription_done",
                "processing_metadata.transcription": processing_metadata,
                "search_text": self._extract_searchable_text(lyrics_path, video_id)
            }
            self.client.update(index="songs", id=video_id, body={"doc": doc_update})
            self.logger.debug(f"[{video_id}] - Successfully updated document with transcription results.")
        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to update document in Elasticsearch. Error: {e}")

    def update_song_with_error(self, video_id: str, error_details: dict):
        if not self.client:
            return
        try:
            error_payload = {
                "status": "failed",
                "error": error_details,
                "updated_at": datetime.utcnow().isoformat()
            }
            self.client.update(index="songs", id=video_id, body={"doc": error_payload})
            self.logger.warning(f"[{video_id}] - Successfully updated document with error details.")
        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to update document with error details. Error: {e}")

    def _extract_searchable_text(self, lyrics_path: str, video_id: str) -> str:
        try:
            with open(lyrics_path, 'r', encoding="utf-8") as f:
                lines = [line for line in f if not line.startswith('[')]
                return " ".join(lines).replace("\n", " ")
        except FileNotFoundError:
            self.logger.error(f"[{video_id}] - Could not extract searchable text. File not found: {lyrics_path}")
            return ""
