"""
Transcription Consumer - Handles transcription processing requests
Complies with architectural mandates and uses shared infrastructure tools
"""
import os
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from shared.kafka.sync_client import KafkaConsumerSync, KafkaProducerSync
from shared.storage import create_file_manager
from shared.utils.logger import Logger

from services.transcriptionService.app.models import (
    KafkaRequestMessage,
    KafkaDoneMessage,
    KafkaFailedMessage,
    ErrorDetails,
    LRCMetadata,
    TranscriptionOutput,
    ElasticsearchSongDocument
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

        # Kafka Topics from environment
        self.request_topic: str = os.getenv("KAFKA_TOPIC_REQUEST", "transcription.process.requested")
        self.done_topic: str = os.getenv("KAFKA_TOPIC_DONE", "transcription.done")
        self.failed_topic: str = os.getenv("KAFKA_TOPIC_FAILED", "transcription.failed")

        bootstrap_servers = os.getenv("KAFKA_BROKER")
        if not bootstrap_servers:
            self.logger.critical("KAFKA_BROKER environment variable not set")
            raise ValueError("KAFKA_BROKER environment variable is required")

        try:
            # Initialize shared Kafka clients
            self.consumer: KafkaConsumerSync = KafkaConsumerSync(
                topics=[self.request_topic],
                bootstrap_servers=bootstrap_servers,
                group_id="transcription-service-group",
                auto_offset_reset='earliest'
            )

            self.producer: KafkaProducerSync = KafkaProducerSync(
                bootstrap_servers=bootstrap_servers
            )

            # Initialize shared file manager
            self.file_manager = create_file_manager(
                storage_type="volume",
                base_path=os.getenv("SHARED_STORAGE_PATH", "/shared")
            )

            # Initialize services
            self.stt_service = SpeechToTextService()
            self.es_updater = ElasticsearchUpdater()

            self.logger.info("TranscriptionConsumer initialized successfully with shared infrastructure")

        except Exception as e:
            self.logger.critical(f"Failed to initialize TranscriptionConsumer. Error: {e}")
            self.logger.error(f"Consumer initialization error details: {str(e)}")
            raise

    def start(self) -> None:
        """Start the transcription consumer"""
        try:
            self.logger.info("Starting TranscriptionConsumer...")
            self.consumer.start()
            self.producer.start()
            self.logger.info(f"TranscriptionConsumer is listening to topic: '{self.request_topic}'")

            # Process messages using consume() generator from shared client
            for msg in self.consumer.consume():
                self._process_message(msg)

        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.critical(f"Critical error in TranscriptionConsumer. Error: {e}")
            self.logger.critical(f"Critical error details: {str(e)}")
        finally:
            self._shutdown()

    def _process_message(self, msg: Dict[str, Any]) -> None:
        """
        Process a single transcription message

        Args:
            msg: Message from Kafka consumer
        """
        video_id: Optional[str] = None

        try:
            # Extract and validate message data
            data = msg.get("value", {})

            # Validate message structure using Pydantic model
            try:
                request_msg = KafkaRequestMessage(**data)
                video_id = request_msg.video_id
            except Exception as validation_error:
                self.logger.warning(f"Invalid message structure received. Error: {validation_error}. Payload: {data}")
                return

            self.logger.info(f"[{video_id}] - Received new transcription request")

            # Step 1: Fetch song document from Elasticsearch
            self.logger.debug(f"[{video_id}] - Fetching song document from Elasticsearch")
            song_doc = self._get_song_document(video_id)
            if not song_doc:
                raise Exception("Song document not found in Elasticsearch")

            # Step 2: Get original audio file path
            original_path = song_doc.file_paths.get("original")
            if not original_path:
                raise Exception("'file_paths.original' not found in song document")

            # Step 3: Transcribe audio file
            self.logger.debug(f"[{video_id}] - Starting audio transcription for file: {original_path}")
            transcription_output = self._transcribe_audio(original_path)
            self.logger.debug(f"[{video_id}] - Transcription finished in {transcription_output.processing_metadata.processing_time} seconds")

            # Step 4: Create LRC file
            lyrics_path = self._create_lrc_file(video_id, transcription_output, song_doc)
            self.logger.debug(f"[{video_id}] - LRC file created at: {lyrics_path}")

            # Step 5: Update Elasticsearch with success
            self._update_elasticsearch_success(video_id, lyrics_path, transcription_output.processing_metadata)
            self.logger.debug(f"[{video_id}] - Elasticsearch document updated with transcription metadata")

            # Step 6: Send success message to Kafka
            self._send_success_message(video_id, transcription_output)
            self.logger.info(f"[{video_id}] - Successfully processed transcription request")

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to process transcription request. Reason: {e}")
            self.logger.error(f"[{video_id}] - Processing error details: {str(e)}")
            self.logger.debug(traceback.format_exc())

            if video_id:
                self._handle_processing_error(video_id, e)

    def _get_song_document(self, video_id: str) -> ElasticsearchSongDocument:
        """
        Get song document from Elasticsearch

        Args:
            video_id: YouTube video ID

        Returns:
            Song document

        Raises:
            Exception: If document not found or retrieval fails
        """
        song_doc = self.es_updater.get_song_document(video_id)
        if not song_doc:
            self.logger.error(f"[{video_id}] - Song document not found in Elasticsearch")
            raise Exception("Song document not found in Elasticsearch")
        return song_doc

    def _transcribe_audio(self, audio_path: str) -> TranscriptionOutput:
        """
        Transcribe audio file using speech-to-text service

        Args:
            audio_path: Path to audio file

        Returns:
            Transcription output with results and metadata

        Raises:
            Exception: If transcription fails
        """
        return self.stt_service.transcribe_audio(audio_path)

    def _create_lrc_file(
        self,
        video_id: str,
        transcription_output: TranscriptionOutput,
        song_doc: ElasticsearchSongDocument
    ) -> str:
        """
        Create LRC file from transcription results

        Args:
            video_id: YouTube video ID
            transcription_output: Transcription results
            song_doc: Song document for metadata

        Returns:
            Path to created LRC file

        Raises:
            Exception: If LRC creation fails
        """
        output_path = f"/shared/audio/{video_id}/lyrics.lrc"

        lrc_metadata = LRCMetadata(
            artist=song_doc.artist,
            title=song_doc.title,
            album=song_doc.album or ""
        )

        return create_lrc_file(
            segments=transcription_output.transcription_result.segments,
            metadata=lrc_metadata,
            output_path=output_path
        )

    def _update_elasticsearch_success(
        self,
        video_id: str,
        lyrics_path: str,
        processing_metadata
    ) -> None:
        """
        Update Elasticsearch with successful transcription results

        Args:
            video_id: YouTube video ID
            lyrics_path: Path to lyrics file
            processing_metadata: Processing metadata

        Raises:
            Exception: If Elasticsearch update fails
        """
        success = self.es_updater.update_song_document(
            video_id=video_id,
            lyrics_path=lyrics_path,
            processing_metadata=processing_metadata
        )

        if not success:
            raise Exception("Failed to update Elasticsearch with transcription results")

    def _send_success_message(self, video_id: str, transcription_output: TranscriptionOutput) -> None:
        """
        Send success message to Kafka

        Args:
            video_id: YouTube video ID
            transcription_output: Transcription results

        Raises:
            Exception: If message sending fails
        """
        metadata = transcription_output.processing_metadata

        # Create structured done message
        done_message = KafkaDoneMessage(
            video_id=video_id,
            status="transcription_done",
            language=metadata.language_detected,
            confidence=metadata.confidence_score,
            word_count=metadata.word_count,
            line_count=metadata.line_count,
            processing_time=metadata.processing_time,
            model_used=metadata.model_used,
            metadata={
                "language_probability": metadata.language_probability,
                "duration_seconds": metadata.duration_seconds
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        # Send message using shared producer
        self.producer.send_message(
            topic=self.done_topic,
            message=done_message.dict(),
            key=video_id
        )

    def _handle_processing_error(self, video_id: str, error: Exception) -> None:
        """
        Handle processing errors by updating Elasticsearch and sending failure message

        Args:
            video_id: YouTube video ID
            error: Exception that occurred
        """
        try:
            # Create error details
            error_details = ErrorDetails(
                code="TRANSCRIPTION_FAILED",
                message=str(error),
                service="transcription_service",
                timestamp=datetime.now(timezone.utc).isoformat(),
                trace=traceback.format_exc()
            )

            # Update Elasticsearch with error
            self.es_updater.update_song_with_error(video_id, error_details)

            # Send failure message to Kafka
            failed_message = KafkaFailedMessage(
                video_id=video_id,
                status="failed",
                error=error_details
            )

            self.producer.send_message(
                topic=self.failed_topic,
                message=failed_message.dict(),
                key=video_id
            )

            self.logger.info(f"[{video_id}] - Failure report sent to Elasticsearch and Kafka")

        except Exception as e:
            self.logger.error(f"[{video_id}] - Failed to handle processing error. Error: {e}")
            self.logger.error(f"[{video_id}] - Error handling error details: {str(e)}")

    def _shutdown(self) -> None:
        """Shutdown the consumer and cleanup resources"""
        try:
            self.logger.info("Shutting down TranscriptionConsumer...")

            if hasattr(self, 'consumer'):
                self.consumer.stop()
                self.logger.debug("Kafka consumer stopped")

            if hasattr(self, 'producer'):
                self.producer.stop()
                self.logger.debug("Kafka producer stopped")

            self.logger.info("TranscriptionConsumer shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during TranscriptionConsumer shutdown. Error: {e}")
            self.logger.error(f"Shutdown error details: {str(e)}")