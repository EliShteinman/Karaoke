from kafka import KafkaConsumer
import json
import os
from app.services.speech_to_text import SpeechToTextService
from app.services.lrc_generator import create_lrc_file
from app.services.elasticsearch_updater import ElasticsearchUpdater

class TranscriptionConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            os.getenv("KAFKA_TOPIC_REQUEST"),
            bootstrap_servers=os.getenv("KAFKA_BROKER"),
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )
        self.stt = SpeechToTextService()
        self.es_updater = ElasticsearchUpdater()

    def start(self):
        for msg in self.consumer:
            data = msg.value
            audio_path = data["original_path"]
            metadata = data.get("metadata", {})
            video_id = data["video_id"]

            # Transcribe
            result = self.stt.transcribe_audio(audio_path)

            # Create LRC
            output_path = f"/shared/audio/{video_id}/lyrics.lrc"
            create_lrc_file(result["segments"], metadata, output_path)

            # Build message
            done_message = {
                "video_id": video_id,
                "status": "transcription_done",
                "lyrics_path": output_path,
                "language": result["language"],
                "duration": result["duration"],
                "word_count": sum(len(seg["text"].split()) for seg in result["segments"]),
                "segments_count": len(result["segments"])
            }

            # Update Elasticsearch
            self.es_updater.update_song_document(video_id, output_path, {
                "language": result["language"],
                "duration": result["duration"],
                "word_count": done_message["word_count"]
            })

            print("✅ Transcription finished:", done_message)
