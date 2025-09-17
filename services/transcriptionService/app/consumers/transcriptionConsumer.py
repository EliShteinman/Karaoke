"""
Transcription Consumer - Handles transcription processing requests
Complies with architectural mandates and uses shared infrastructure tools
"""
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from shared.kafka.sync_client import KafkaConsumerSync, KafkaProducerSync
from shared.storage.file_storage import create_file_manager
from shared.utils.logger import Logger

# Import config and models
from services.transcriptionService.app.services.config import TranscriptionServiceConfig
from services.transcriptionService.app.models import (
    KafkaRequestMessage,
    KafkaDoneMessage,
    KafkaFailedMessage,
    ErrorDetails,
    LRCMetadata,
    TranscriptionOutput,
    ElasticsearchSongDocument,
    ProcessingMetadata
)
from services.transcriptionService.app.services.elasticsearch_updater import ElasticsearchUpdater
from services.transcriptionService.app.services.lrc_generator import create_lrc_file
from services.transcriptionService.app.services.speech_to_text import SpeechToTextService


class TranscriptionConsumer:
    """
    Main consumer for transcription processing
    Handles Kafka messages and orchestrates the transcription pipeline
    """

    def __init__(self) -> None:
        self.logger = Logger.get_logger(__name__)
        self.config = TranscriptionServiceConfig()

        try:
            self.consumer: KafkaConsumerSync = KafkaConsumerSync(
                topics=[self.config.kafka_topic_transcription_requested],
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                group_id=self.config.kafka_consumer_group,
                auto_offset_reset='earliest',
                consumer_timeout_ms=-1  # Disable timeout for continuous listening
            )
            self.producer: KafkaProducerSync = KafkaProducerSync(
                bootstrap_servers=self.config.kafka_bootstrap_servers
            )
            self.file_manager = create_file_manager(
                storage_type="volume",
                base_path=self.config.storage_base_path
            )
            self.stt_service = SpeechToTextService()
            self.es_updater = ElasticsearchUpdater()
            self.logger.info("TranscriptionConsumer initialized successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize TranscriptionConsumer. Error: {e}")
            raise

    def start(self) -> None:
        try:
            self.logger.info("Starting TranscriptionConsumer...")
            self.consumer.start()
            self.producer.start()
            self.logger.info(f"Listening to topic: '{self.config.kafka_topic_transcription_requested}'")

            # Continuous message processing loop
            for msg in self.consumer.consume():
                try:
                    self._process_message(msg)
                except Exception as msg_error:
                    # Log individual message processing errors but continue the loop
                    self.logger.error(f"Error processing individual message: {msg_error}")
                    self.logger.debug(f"Message processing error traceback: {traceback.format_exc()}")
                    # Continue to next message - don't break the entire consumer loop
                    continue

        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received.")
        except Exception as e:
            self.logger.critical(f"Critical error in consumer loop. Error: {e}")
            self.logger.debug(f"Consumer loop error traceback: {traceback.format_exc()}")
            # Re-raise critical errors that should stop the entire service
            raise
        finally:
            self._shutdown()

    def _process_message(self, msg: Dict[str, Any]) -> None:
        video_id: Optional[str] = None
        try:
            self.logger.debug(f"Raw message received: {msg}")
            message_value = msg.get("value", {})

            # Extract data from the nested 'data' field in the message
            data = message_value.get("data", {})
            if not data:
                self.logger.warning(f"No 'data' field found in message. Full payload: {message_value}")
                return

            try:
                request_msg = KafkaRequestMessage(**data)
                video_id = request_msg.video_id
                self.logger.debug(f"[{video_id}] - Message validated successfully.")
            except Exception as validation_error:
                self.logger.warning(f"Invalid message structure. Error: {validation_error}. Message data: {data}")
                return

            self.logger.info(f"[{video_id}] - Processing new transcription request.")

            song_doc = self._get_song_document(video_id)
            original_path = song_doc.file_paths.get("original")
            if not original_path:
                raise Exception("'file_paths.original' not found in song document")
            self.logger.debug(f"[{video_id}] - Original audio path: {original_path}")

            # Step 3: Update status to indicate transcription started
            self.es_updater.update_status_field(video_id, "transcription", "in_progress")
            self.logger.debug(f"[{video_id}] - Updated transcription status to 'in_progress'")

            # Step 4: Transcribe audio file
            transcription_output = self._transcribe_audio(original_path, video_id)

            # Step 5: Create LRC file
            lyrics_path = self._create_lrc_file(video_id, transcription_output, song_doc)
            self.logger.debug(f"[{video_id}] - LRC file created at: {lyrics_path}")

            # Step 6: Update Elasticsearch with success
            self._update_elasticsearch_success(video_id, lyrics_path, transcription_output.processing_metadata)
            self.logger.debug(f"[{video_id}] - Elasticsearch document updated with transcription metadata")

            # Step 7: Send success message to Kafka
            self._send_success_message(video_id, transcription_output)
            
            self.logger.info(f"[{video_id}] - Successfully processed transcription request.")

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to process request. Reason: {e}")
            self.logger.debug(traceback.format_exc())
            if video_id:
                self._handle_processing_error(video_id, e)

    def _get_song_document(self, video_id: str) -> ElasticsearchSongDocument:
        self.logger.debug(f"[{video_id}] - Step 1: Fetching song document from Elasticsearch.")
        song_doc = self.es_updater.get_song_document(video_id)
        if not song_doc:
            raise Exception("Song document not found in Elasticsearch")
        self.logger.debug(f"[{video_id}] - Song document retrieved successfully. Title: {song_doc.title}")
        return song_doc

    def _transcribe_audio(self, audio_path: str, video_id: str) -> TranscriptionOutput:
        self.logger.debug(f"[{video_id}] - Step 2: Starting audio transcription.")
        transcription_output = self.stt_service.transcribe_audio(audio_path)
        self.logger.debug(f"[{video_id}] - Transcription finished. Detected language: {transcription_output.processing_metadata.language_detected}")
        return transcription_output

    def _create_lrc_file(self, video_id: str, transcription_output: TranscriptionOutput, song_doc: ElasticsearchSongDocument) -> str:
        self.logger.debug(f"[{video_id}] - Step 3: Creating LRC file.")
        output_path = f"{self.config.storage_base_path}/audio/{video_id}/lyrics.lrc"
        lrc_metadata = LRCMetadata(artist=song_doc.artist, title=song_doc.title, album=song_doc.album or "")
        created_path = create_lrc_file(segments=transcription_output.transcription_result.segments, metadata=lrc_metadata, output_path=output_path)
        self.logger.debug(f"[{video_id}] - LRC file created at: {created_path}")
        return created_path

    def _update_elasticsearch_success(self, video_id: str, lyrics_path: str, processing_metadata: ProcessingMetadata) -> None:
        self.logger.debug(f"[{video_id}] - Step 4: Updating Elasticsearch with results.")
        success = self.es_updater.update_song_document(video_id=video_id, lyrics_path=lyrics_path, processing_metadata=processing_metadata)
        if not success:
            raise Exception("Failed to update Elasticsearch with transcription results")
        self.logger.debug(f"[{video_id}] - Elasticsearch document updated successfully.")

    def _send_success_message(self, video_id: str, transcription_output: TranscriptionOutput) -> None:
        self.logger.debug(f"[{video_id}] - Step 5: Sending success message to Kafka.")
        metadata = transcription_output.processing_metadata
        done_message = KafkaDoneMessage(
            video_id=video_id, status="transcription_done", language=metadata.language_detected,
            confidence=metadata.confidence_score, word_count=metadata.word_count, line_count=metadata.line_count,
            processing_time=metadata.processing_time, model_used=metadata.model_used,
            metadata={"language_probability": metadata.language_probability, "duration_seconds": metadata.duration_seconds},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.logger.debug(f"[{video_id}] - Sending done message: {done_message.dict()}")
        self.producer.send_message(topic=self.config.kafka_topic_transcription_done, message=done_message.dict(), key=video_id)
        self.logger.debug(f"[{video_id}] - Success message sent to Kafka.")

    def _handle_processing_error(self, video_id: str, error: Exception) -> None:
        try:
            self.logger.warning(f"[{video_id}] - Handling processing error: {error}")
            error_details = ErrorDetails(
                code="TRANSCRIPTION_FAILED", message=str(error), service="transcription_service",
                timestamp=datetime.now(timezone.utc).isoformat(), trace=traceback.format_exc()
            )
            self.logger.debug(f"[{video_id}] - Updating Elasticsearch with error details.")
            self.es_updater.update_song_with_error(video_id, error_details)
            
            failed_message = KafkaFailedMessage(video_id=video_id, status="failed", error=error_details)
            self.logger.debug(f"[{video_id}] - Sending failure message to Kafka: {failed_message.dict()}")
            self.producer.send_message(topic=self.config.kafka_topic_transcription_failed, message=failed_message.dict(), key=video_id)
            
            self.logger.info(f"[{video_id}] - Failure report sent successfully.")
        except Exception as e:
            self.logger.critical(f"[{video_id}] - FAILED TO HANDLE ERROR. Final error: {e}")

    def shutdown(self) -> None:
        """Public method for graceful shutdown"""
        self._shutdown()

    def _shutdown(self) -> None:
        try:
            self.logger.info("Shutting down TranscriptionConsumer...")
            if hasattr(self, 'consumer'): self.consumer.stop()
            if hasattr(self, 'producer'): self.producer.stop()
            self.logger.info("Shutdown complete.")
        except Exception as e:
            self.logger.error(f"Error during shutdown. Error: {e}")
