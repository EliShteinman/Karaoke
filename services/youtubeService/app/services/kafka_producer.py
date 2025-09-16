from typing import Dict, Any
from services.youtubeService.app.config.config import config
from shared.kafka.sync_client import KafkaProducerSync
from shared.utils.logger import Logger


class YouTubeServiceKafkaProducer:
    """
    Kafka producer specifically for YouTube Service
    Handles sending messages to various topics as per schema requirements
    """

    def __init__(self, bootstrap_servers: str = config.KAFKA_BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers

        # Initialize logger with proper configuration
        logger_config = config.get_logger_config()
        logger_config["name"] = "youtube_service.kafka_producer"
        self.logger = Logger.get_logger(**logger_config)

        self.producer = KafkaProducerSync(bootstrap_servers=bootstrap_servers)
        self.logger.info("YouTubeServiceKafkaProducer initialized")

    def start(self) -> None:
        """Start the Kafka producer"""
        try:
            self.producer.start()
            self.logger.info("Kafka producer started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Kafka producer: {e}")
            raise

    def stop(self) -> None:
        """Stop the Kafka producer"""
        try:
            self.producer.stop()
            self.logger.info("Kafka producer stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping Kafka producer: {e}")

    def send_song_downloaded(self, message: Dict[str, Any]) -> bool:
        """Send song downloaded event"""
        self.logger.info(f"Sending song downloaded event for video_id: {message.get('video_id')}")
        return self._send_message("song.downloaded", message)

    def send_audio_process_request(self, message: Dict[str, Any]) -> bool:
        """Send audio processing request (only video_id)"""
        self.logger.info(f"Sending audio process request for video_id: {message.get('video_id')}")
        return self._send_message("audio.process.requested", message)

    def send_transcription_request(self, message: Dict[str, Any]) -> bool:
        """Send transcription request (only video_id)"""
        self.logger.info(f"Sending transcription request for video_id: {message.get('video_id')}")
        return self._send_message("transcription.process.requested", message)

    def send_download_failed(self, message: Dict[str, Any]) -> bool:
        """Send download failed event"""
        self.logger.error(f"Sending download failed event for video_id: {message.get('video_id')}")
        return self._send_message("song.download.failed", message)

    def _send_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """Send message to specified topic"""
        try:
            success = self.producer.send_message(topic, message)
            if success:
                self.logger.info(f"Message sent successfully to topic '{topic}'")
            else:
                self.logger.error(f"Failed to send message to topic '{topic}'")
            return success
        except Exception as e:
            self.logger.error(f"Error sending message to topic '{topic}': {e}")
            return False

    def send_batch_messages(self, messages: list) -> int:
        """
        Send multiple messages in batch
        Each message should be a tuple of (topic, message_data)
        """
        successful_sends = 0
        try:
            self.start()
            for topic, message_data in messages:
                if self._send_message(topic, message_data):
                    successful_sends += 1

            self.logger.info(f"Batch send completed: {successful_sends}/{len(messages)} messages sent")
            return successful_sends

        except Exception as e:
            self.logger.error(f"Error in batch message sending: {e}")
            return successful_sends
        finally:
            self.stop()