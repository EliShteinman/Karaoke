import json
import os
import traceback
from datetime import datetime

from kafka import KafkaConsumer

from shared.utils.logger import Logger
from ..services.speech_to_text import SpeechToTextService
from ..services.lrc_generator import create_lrc_file
from ..services.elasticsearch_updater import ElasticsearchUpdater
from ..utils.kafka_producer import KafkaProducerManager

class TranscriptionConsumer:
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        
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
        self.logger.info(f"TranscriptionConsumer is listening to topic: '{self.request_topic}'")
        try:
            for msg in self.consumer:
                video_id = None # Initialize for error handling
                try:
                    data = msg.value
                    video_id = data.get("video_id")

                    if not video_id:
                        self.logger.warning(f"Message received with no video_id. Discarding. Payload: {data}")
                        continue

                    self.logger.info(f"[{video_id}] - Received new transcription request.")

                    # 1. Fetch song document from Elasticsearch
                    self.logger.debug(f"[{video_id}] - Fetching song document from Elasticsearch.")
                    song_doc = self.es_updater.get_song_document(video_id)
                    if not song_doc:
                        raise Exception(f"Song document not found in Elasticsearch.")

                    original_path = song_doc.get("file_paths", {}).get("original")
                    if not original_path:
                        raise Exception(f"'file_paths.original' not found in song document.")

                    # 2. Transcribe audio file
                    self.logger.debug(f"[{video_id}] - Starting audio transcription for file: {original_path}")
                    transcription_output = self.stt.transcribe_audio(original_path)
                    result = transcription_output["transcription_result"]
                    metadata = transcription_output["processing_metadata"]
                    self.logger.debug(f"[{video_id}] - Transcription finished in {metadata['processing_time']} seconds.")

                    # 3. Create LRC file
                    output_path = f"/shared/audio/{video_id}/lyrics.lrc"
                    lrc_metadata = {
                        'artist': song_doc.get('artist', ''),
                        'title': song_doc.get('title', ''),
                        'album': song_doc.get('album', '')
                    }
                    create_lrc_file(result["segments"], lrc_metadata, output_path)
                    self.logger.debug(f"[{video_id}] - LRC file created at: {output_path}")

                    # 4. Update Elasticsearch with success
                    self.es_updater.update_song_document(video_id, output_path, metadata)
                    self.logger.debug(f"[{video_id}] - Elasticsearch document updated with transcription metadata.")

                    # 5. Send success message to Kafka
                    done_message = {
                        "video_id": video_id,
                        "status": "transcription_done",
                        "timestamp": datetime.utcnow().isoformat(),
                        **metadata
                    }
                    self.producer.send_message(self.done_topic, done_message)
                    self.logger.info(f"[{video_id}] - Successfully processed transcription request.")

                except Exception as e:
                    self.logger.error(f"[{video_id}] - Failed to process transcription request. Reason: {e}")
                    self.logger.debug(traceback.format_exc()) # Log stack trace for debugging

                    if video_id:
                        error_details = {
                            "code": "TRANSCRIPTION_FAILED",
                            "message": str(e),
                            "service": "transcription_service",
                            "timestamp": datetime.utcnow().isoformat(),
                            "trace": traceback.format_exc()
                        }
                        self.es_updater.update_song_with_error(video_id, error_details)
                        self.producer.send_message(self.failed_topic, {"video_id": video_id, "status": "failed", "error": error_details})
                        self.logger.info(f"[{video_id}] - Failure report sent to Elasticsearch and Kafka.")

        finally:
            self.logger.info("Shutting down TranscriptionConsumer and Kafka producer.")
            self.consumer.close()
            self.producer.close()
