from datetime import datetime
from elasticsearch import Elasticsearch
import os

class ElasticsearchUpdater:
    def __init__(self):
        self.client = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_HOST")])

    def update_song_document(self, video_id, lyrics_path, transcription_metadata):
        doc_update = {
            "file_paths.lyrics": lyrics_path,
            "updated_at": datetime.utcnow().isoformat(),
            "transcription_metadata": transcription_metadata,
            "search_text": self._extract_searchable_text(lyrics_path)
        }
        self.client.update(index="songs", id=video_id, body={"doc": doc_update})

    def _extract_searchable_text(self, lyrics_path):
        with open(lyrics_path, encoding="utf-8") as f:
            return f.read().replace("\n", " ")
