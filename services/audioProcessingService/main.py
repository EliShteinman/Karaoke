"""
Audio Processing Service - Main Entry Point

This service listens to Kafka for audio processing requests containing only video_id,
retrieves file paths from Elasticsearch, processes audio files to create dual output
(vocals removed and vocals only), and updates Elasticsearch with the results.

Architecture compliance:
- Uses shared library for all infrastructure access
- Receives only video_id from Kafka (no file paths)
- Retrieves file paths from Elasticsearch
- Uses iterative consumption model instead of callback for better code flow
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
from shared.storage.file_storage import create_file_manager
from shared.utils.data_utils import normalize_elasticsearch_song_document
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

        # Initialize file manager for standardized path handling
        self.file_manager = create_file_manager(
            storage_type="volume",
            base_path=self.config.storage_base_path
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

            # Start continuous message consumption using iterative model with retry loop
            logger.info("Starting continuous message consumption...")
            processed_count = 0

            while True:
                try:
                    logger.info("🔄 Starting new consumption cycle - listening for audio processing messages...")
                    for message in self.kafka_consumer.consume():
                        try:
                            # Process each message
                            success = self._process_message(message)
                            if success:
                                processed_count += 1
                                logger.info(f"✅ Successfully processed message from '{message['topic']}' - returning to listen for more...")
                            else:
                                logger.warning(f"❌ Failed to process message from '{message['topic']}' - returning to listen for more...")

                        except Exception as e:
                            logger.error(f"Error processing individual message: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Consumer loop error: {e}")
                    logger.info("Restarting consumer loop in 5 seconds...")
                    import time
                    time.sleep(5)
                    continue

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
            # Extract video_id from message - it's nested in the "data" field
            message_data = message["value"].get("data", {})
            video_id = message_data.get("video_id")

            if not video_id:
                logger.error(f"No video_id found in message data. Full message: {message}")
                logger.error(f"Expected structure: message['value']['data']['video_id']")
                return False

            logger.info(f"Processing audio for video_id: {video_id}")

            # Process the audio file
            return self._process_audio_file(video_id)

        except Exception as e:
            logger.error(f"Error processing message {message}: {e}")
            # Try to extract video_id for error reporting
            try:
                message_data = message["value"].get("data", {})
                video_id = message_data.get("video_id")
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
            raw_song_doc = self.song_repo.get_song(video_id)
            if not raw_song_doc:
                self._report_error(video_id, "SONG_NOT_FOUND", f"Song document not found for video_id: {video_id}")
                return False

            # Normalize the document to handle flat vs nested structure
            song_doc = normalize_elasticsearch_song_document(raw_song_doc)

            file_paths = song_doc.get("file_paths", {})
            original_relative_path = file_paths.get("original")

            if not original_relative_path:
                self._report_error(video_id, "ORIGINAL_FILE_NOT_FOUND", f"Original file path not found for video_id: {video_id}")
                return False

            # Use file manager to get absolute path - this handles cross-platform consistency
            try:
                original_absolute_path = self.file_manager.get_full_path(original_relative_path)
                if not self.file_manager.storage.file_exists(original_relative_path):
                    self._report_error(video_id, "ORIGINAL_FILE_MISSING", f"Original file does not exist: {original_absolute_path}")
                    return False
            except Exception as e:
                self._report_error(video_id, "PATH_RESOLUTION_ERROR", f"Failed to resolve file path: {original_relative_path}, error: {str(e)}")
                return False

            logger.info(f"Found original file at: {original_absolute_path}")

            # Use file manager to get standardized output paths for both files
            vocals_removed_relative = self.file_manager.get_relative_path_vocals_removed(video_id)
            vocals_relative = self.file_manager.get_relative_path_vocals(video_id)
            vocals_removed_absolute = self.file_manager.get_full_path(vocals_removed_relative)
            vocals_absolute = self.file_manager.get_full_path(vocals_relative)
            output_dir = os.path.dirname(vocals_removed_absolute)

            logger.info(f"Processing {original_absolute_path} -> dual output:")
            logger.info(f"  - Vocals removed: {vocals_removed_absolute}")
            logger.info(f"  - Vocals only: {vocals_absolute}")

            # Perform vocal separation
            processing_start = datetime.now()
            try:
                logger.info(f"Starting Demucs audio separation for {video_id}...")
                logger.info(f"Input file size: {os.path.getsize(original_absolute_path)} bytes")

                vocals_removed_result, vocals_only_result = separate_vocals(original_absolute_path, save_path=output_dir)
                processing_time = (datetime.now() - processing_start).total_seconds()

                logger.info(f"Demucs separation completed successfully in {processing_time:.2f}s")
                logger.info(f"Created dual output files:")
                logger.info(f"  - Instrumental: {vocals_removed_result}")
                logger.info(f"  - Vocals: {vocals_only_result}")

                # Verify the results match our expected paths
                if vocals_removed_result != vocals_removed_absolute:
                    logger.warning(f"Demucs vocals_removed output path {vocals_removed_result} differs from expected {vocals_removed_absolute}")
                if vocals_only_result != vocals_absolute:
                    logger.warning(f"Demucs vocals output path {vocals_only_result} differs from expected {vocals_absolute}")

                vocals_removed_path = vocals_removed_result
                vocals_path = vocals_only_result

            except Exception as e:
                processing_time = (datetime.now() - processing_start).total_seconds()
                logger.error(f"Vocal separation failed after {processing_time:.2f}s: {e}")
                self._report_error(video_id, "VOCAL_SEPARATION_FAILED", f"Demucs processing failed: {str(e)}")
                return False

            # Verify both output files were created and have reasonable sizes
            if not os.path.exists(vocals_removed_path):
                self._report_error(video_id, "VOCALS_REMOVED_FILE_NOT_CREATED", "Vocal separation failed - vocals_removed.wav not created")
                return False

            if not os.path.exists(vocals_path):
                self._report_error(video_id, "VOCALS_FILE_NOT_CREATED", "Vocal separation failed - vocals.wav not created")
                return False

            # Quality gate: check if output files have reasonable sizes
            original_size = os.path.getsize(original_absolute_path)
            vocals_removed_size = os.path.getsize(vocals_removed_path)
            vocals_size = os.path.getsize(vocals_path)

            logger.info(f"File sizes comparison:")
            logger.info(f"  - Original: {original_size:,} bytes")
            logger.info(f"  - Vocals removed: {vocals_removed_size:,} bytes")
            logger.info(f"  - Vocals only: {vocals_size:,} bytes")

            # Check if files are suspiciously small
            if vocals_removed_size < (original_size * 0.05):  # Less than 5% seems suspicious
                self._report_error(video_id, "VOCALS_REMOVED_FILE_TOO_SMALL", f"Vocals removed file suspiciously small: {vocals_removed_size} bytes vs original {original_size} bytes")
                return False

            if vocals_size < (original_size * 0.05):  # Less than 5% seems suspicious
                self._report_error(video_id, "VOCALS_FILE_TOO_SMALL", f"Vocals file suspiciously small: {vocals_size} bytes vs original {original_size} bytes")
                return False

            # Update Elasticsearch with success - store both relative paths
            logger.info(f"Updating Elasticsearch with dual file paths for {video_id}")
            self.song_repo.update_file_path(video_id, "vocals_removed", vocals_removed_relative)
            self.song_repo.update_file_path(video_id, "vocals", vocals_relative)

            # Update processing metadata with both file information
            metadata = {
                "audio": {
                    "processing_time": processing_time,
                    "original_size": original_size,
                    "vocals_removed_size": vocals_removed_size,
                    "vocals_size": vocals_size,
                    "algorithm": "demucs_htdemucs",
                    "separation_quality": "ml_based",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            self.song_repo.update_metadata(video_id, metadata)
            logger.info(f"Updated Elasticsearch metadata with processing info")

            # Update status to completed (this will auto-check overall completion)
            self.song_repo.update_status_and_check_completion(video_id, "audio_processing", "completed")

            # Send completion event to Kafka
            self._send_completion_event(video_id, processing_time)

            logger.info(f"🎵 Successfully completed dual audio processing for {video_id}")
            logger.info(f"📊 Processing summary:")
            logger.info(f"   ⏱️  Duration: {processing_time:.2f}s")
            logger.info(f"   📁 Files created: vocals_removed.wav ({vocals_removed_size:,} bytes), vocals.wav ({vocals_size:,} bytes)")
            logger.info(f"   🎯 Algorithm: Demucs ML separation")
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
                "algorithm_used": "demucs_htdemucs"
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


