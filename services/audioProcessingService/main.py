"""
Audio Processing Service - Main Entry Point

This service listens to Kafka for audio processing requests containing only video_id,
retrieves file paths from Elasticsearch, processes audio files to remove vocals,
and updates Elasticsearch with the results.

Architecture compliance:
- Uses shared library for all infrastructure access
- Receives only video_id from Kafka (no file paths)
- Retrieves file paths from Elasticsearch
- Uses proper error handling and logging
- Updates status in Elasticsearch with detailed progress
- Sends completion/error events to Kafka
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime, timezone

from shared.kafka.sync_client import KafkaConsumerSync, KafkaProducerSync
from shared.repositories.factory import RepositoryFactory
from shared.utils.logger import Logger
from services.audioProcessingService.config import AudioProcessingServiceConfig
from services.audioProcessingService.Audio_separation import separate_vocals

# Initialize logging
logger = Logger.get_logger(__name__)

class AudioProcessingService:
    """
    Audio Processing Service for removing vocals from audio files.

    Follows the architectural principles:
    - Single Source of Truth: Gets file paths only from Elasticsearch
    - Kafka contains only video_id
    - Proper error handling and status updates
    - Continuous daemon operation
    """

    def __init__(self):
        self.config = AudioProcessingServiceConfig()

        # Validate configuration
        try:
            self.config.validate_config()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

        # Initialize Kafka consumer with correct settings for continuous listening
        self.kafka_consumer = KafkaConsumerSync(
            topics=[self.config.kafka_topic_audio_requested],
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            group_id=self.config.kafka_consumer_group,
            auto_offset_reset='earliest',
            consumer_timeout_ms=-1  # Disable timeout for continuous listening
        )

        # Initialize Kafka producer for completion/error messages
        self.kafka_producer = KafkaProducerSync(
            bootstrap_servers=self.config.kafka_bootstrap_servers
        )

        # Initialize song repository using shared library
        self.song_repo = RepositoryFactory.create_song_repository_from_params(
            elasticsearch_host=self.config.elasticsearch_host,
            elasticsearch_port=self.config.elasticsearch_port,
            elasticsearch_scheme=self.config.elasticsearch_scheme,
            songs_index=self.config.elasticsearch_songs_index,
            async_mode=False
        )

        logger.info("Audio Processing Service initialized successfully")

    def start(self) -> None:
        """Start the service as a continuous daemon"""
        logger.info("Starting Audio Processing Service daemon...")

        try:
            # Start Kafka components
            self.kafka_consumer.start()
            self.kafka_producer.start()
            logger.info("Kafka components started successfully")

            # Start continuous listening - this will run forever
            logger.info("Starting continuous message listening...")
            processed_count = self.kafka_consumer.listen_forever(
                message_handler=self._process_message,
                max_messages=None  # Run forever
            )

            logger.info(f"Service stopped after processing {processed_count} messages")

        except KeyboardInterrupt:
            logger.info("Service interrupted by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Critical error in service: {e}")
            # Log full traceback for debugging
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
        finally:
            self._shutdown()

    def _process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a single message from Kafka.
        Each message processing is wrapped in try-catch to prevent service failure.

        Args:
            message: Kafka message containing video_id

        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Extract video_id from message
            video_id = message["value"].get("video_id")
            if not video_id:
                logger.error(f"No video_id found in message: {message}")
                return False

            logger.info(f"Processing audio for video_id: {video_id}")

            # Process the audio file
            return self._process_audio_file(video_id)

        except Exception as e:
            logger.error(f"Error processing message {message}: {e}")
            # Try to extract video_id for error reporting
            try:
                video_id = message["value"].get("video_id")
                if video_id:
                    self._report_error(video_id, "MESSAGE_PROCESSING_ERROR", str(e))
            except:
                pass
            return False

    def _process_audio_file(self, video_id: str) -> bool:
        """
        Process audio file for a given video_id.

        Args:
            video_id: The video ID to process

        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Update status to in_progress
            self.song_repo.update_status_field(video_id, "audio_processing", "in_progress")
            logger.info(f"Started audio processing for {video_id}")

            # Get original file path from Elasticsearch
            song_doc = self.song_repo.get_song(video_id)
            if not song_doc:
                self._report_error(video_id, "SONG_NOT_FOUND", f"Song document not found for video_id: {video_id}")
                return False

            file_paths = song_doc.get("file_paths", {})
            original_path = file_paths.get("original")

            if not original_path:
                self._report_error(video_id, "ORIGINAL_FILE_NOT_FOUND", f"Original file path not found for video_id: {video_id}")
                return False

            # Verify original file exists
            if not os.path.exists(original_path):
                self._report_error(video_id, "ORIGINAL_FILE_MISSING", f"Original file does not exist: {original_path}")
                return False

            # Define output path with fixed filename
            output_dir = os.path.dirname(original_path)
            vocals_removed_path = os.path.join(output_dir, "vocals_removed.mp3")

            logger.info(f"Processing {original_path} -> {vocals_removed_path}")

            # Perform vocal separation
            processing_start = datetime.now()
            separate_vocals(original_path, save_path=output_dir)
            processing_time = (datetime.now() - processing_start).total_seconds()

            # Verify output file was created and has reasonable size
            if not os.path.exists(vocals_removed_path):
                self._report_error(video_id, "OUTPUT_FILE_NOT_CREATED", "Vocal separation failed - output file not created")
                return False

            # Quality gate: check if output file is reasonable size
            original_size = os.path.getsize(original_path)
            output_size = os.path.getsize(vocals_removed_path)

            if output_size < (original_size * 0.1):  # Less than 10% of original size seems suspicious
                self._report_error(video_id, "OUTPUT_FILE_TOO_SMALL", f"Output file suspiciously small: {output_size} bytes vs original {original_size} bytes")
                return False

            # Update Elasticsearch with success
            self.song_repo.update_file_path(video_id, "vocals_removed", vocals_removed_path)

            # Update processing metadata
            metadata = {
                "audio": {
                    "processing_time": processing_time,
                    "original_size": original_size,
                    "processed_size": output_size,
                    "algorithm": "center_channel_extraction",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            self.song_repo.update_metadata(video_id, metadata)

            # Update status to completed (this will auto-check overall completion)
            self.song_repo.update_status_and_check_completion(video_id, "audio_processing", "completed")

            # Send completion event to Kafka
            self._send_completion_event(video_id, processing_time)

            logger.info(f"Successfully completed audio processing for {video_id} in {processing_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"Error processing audio for {video_id}: {e}")
            self._report_error(video_id, "AUDIO_PROCESSING_FAILED", str(e))
            return False

    def _report_error(self, video_id: str, error_code: str, error_message: str) -> None:
        """Report error to Elasticsearch and Kafka"""
        try:
            # Update Elasticsearch with error
            self.song_repo.mark_song_failed(
                video_id=video_id,
                error_code=error_code,
                error_message=error_message,
                service="audio_processing_service",
                failed_step="audio_processing"
            )

            # Send error event to Kafka
            error_message_data = {
                "video_id": video_id,
                "status": "failed",
                "error": {
                    "code": error_code,
                    "message": error_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "service": "audio_processing_service"
                }
            }

            self.kafka_producer.send_message(self.config.kafka_topic_audio_failed, error_message_data)
            logger.error(f"Reported error for {video_id}: {error_code} - {error_message}")

        except Exception as e:
            logger.error(f"Failed to report error for {video_id}: {e}")

    def _send_completion_event(self, video_id: str, processing_time: float) -> None:
        """Send completion event to Kafka"""
        try:
            completion_message = {
                "video_id": video_id,
                "status": "vocals_processed",
                "processing_time": processing_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "algorithm_used": "center_channel_extraction"
            }

            self.kafka_producer.send_message(self.config.kafka_topic_audio_processed, completion_message)
            logger.info(f"Sent completion event for {video_id}")

        except Exception as e:
            logger.error(f"Failed to send completion event for {video_id}: {e}")

    def _shutdown(self) -> None:
        """Gracefully shutdown the service"""
        logger.info("Shutting down Audio Processing Service...")
        try:
            self.kafka_consumer.stop()
            self.kafka_producer.stop()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        logger.info("Audio Processing Service stopped")


if __name__ == "__main__":
    service = AudioProcessingService()
    service.start()


