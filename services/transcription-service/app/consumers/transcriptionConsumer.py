import json
import os
import traceback
from datetime import datetime

from kafka import KafkaConsumer

from ..services.speech_to_text import SpeechToTextService
from ..services.lrc_generator import create_lrc_file
from ..services.elasticsearch_updater import ElasticsearchUpdater
from ..utils.kafka_producer import KafkaProducerManager

class TranscriptionConsumer:
    def __init__(self):
        # Kafka Topics
        self.request_topic = os.getenv("KAFKA_TOPIC_REQUEST", "transcription.process.requested")
        self.done_topic = os.getenv("KAFKA_TOPIC_DONE", "transcription.done")
        self.failed_topic = os.getenv("KAFKA_TOPIC_FAILED", "transcription.failed")

        # Kafka Consumer
        self.consumer = KafkaConsumer(
            self.request_topic,
            bootstrap_servers=os.getenv("KAFKA_BROKER"),
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset='earliest',
            group_id="transcription-service-group"
        )
        
        # Kafka Producer
        self.producer = KafkaProducerManager()
        
        # Services
        self.stt = SpeechToTextService()
        self.es_updater = ElasticsearchUpdater()

    def start(self):
        print(f"\n✅ TranscriptionConsumer is listening to topic: '{self.request_topic}'\n")
        try:
            for msg in self.consumer:
                video_id = None # Initialize for error handling
                try:
                    data = msg.value
                    video_id = data.get("video_id")

                    if not video_id:
                        print(f"ERROR: Message received with no video_id. Payload: {data}")
                        continue

                    print(f"INFO: Processing video_id: {video_id}")

                    # 1. Fetch song document from Elasticsearch
                    song_doc = self.es_updater.get_song_document(video_id)
                    if not song_doc:
                        raise Exception(f"Song document not found in Elasticsearch for video_id: {video_id}")

                    original_path = song_doc.get("file_paths", {}).get("original")
                    if not original_path:
                        raise Exception(f"'file_paths.original' not found in song document for video_id: {video_id}")

                    # 2. Transcribe audio file
                    transcription_output = self.stt.transcribe_audio(original_path)
                    result = transcription_output["transcription_result"]
                    metadata = transcription_output["processing_metadata"]

                    # 3. Create LRC file
                    output_path = f"/shared/audio/{video_id}/lyrics.lrc"
                    lrc_metadata = {
                        'artist': song_doc.get('artist', ''),
                        'title': song_doc.get('title', ''),
                        'album': song_doc.get('album', '')
                    }
                    create_lrc_file(result["segments"], lrc_metadata, output_path)

                    # 4. Update Elasticsearch with success
                    self.es_updater.update_song_document(video_id, output_path, metadata)

                    # 5. Send success message to Kafka
                    done_message = {
                        "video_id": video_id,
                        "status": "transcription_done",
                        "timestamp": datetime.utcnow().isoformat(),
                        **metadata # Unpack all processing metadata
                    }
                    self.producer.send_message(self.done_topic, done_message)
                    print(f"✅ SUCCESS: Finished processing video_id: {video_id}")

                except Exception as e:
                    print(f"❌ ERROR: Failed to process video_id: {video_id}. Reason: {e}")
                    traceback.print_exc()

                    if video_id: # Only if we have a video_id can we report the failure
                        error_details = {
                            "code": "TRANSCRIPTION_FAILED",
                            "message": str(e),
                            "service": "transcription_service",
                            "timestamp": datetime.utcnow().isoformat(),
                            "trace": traceback.format_exc()
                        }
                        # Update ES with error
                        self.es_updater.update_song_with_error(video_id, error_details)
                        # Send error message to Kafka
                        self.producer.send_message(self.failed_topic, {"video_id": video_id, "status": "failed", "error": error_details})

        finally:
            print("\nINFO: Shutting down TranscriptionConsumer and Kafka producer.")
            self.consumer.close()
            self.producer.close()
