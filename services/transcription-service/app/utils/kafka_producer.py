import json
import os
from kafka import KafkaProducer
from shared.utils.logger import Logger

class KafkaProducerManager:
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.producer = None
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=os.getenv("KAFKA_BROKER"),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks='all', # Ensure messages are received by all replicas
                retries=3,   # Retry sending messages on failure
            )
        except Exception as e:
            self.logger.critical(f"Failed to initialize Kafka Producer. Error: {e}")
            # Re-raise the exception to prevent the application from starting with a broken producer
            raise

    def send_message(self, topic: str, message: dict):
        if not self.producer:
            self.logger.error("Cannot send message: Kafka Producer is not initialized.")
            return
            
        try:
            video_id = message.get("video_id", "N/A")
            self.logger.debug(f"[{video_id}] - Sending message to Kafka topic '{topic}'.")
            self.producer.send(topic, message)
        except Exception as e:
            self.logger.error(f"Could not send message to Kafka topic '{topic}'. Reason: {e}")

    def close(self):
        if self.producer:
            self.logger.info("Flushing and closing Kafka producer.")
            self.producer.flush() # Ensure all buffered messages are sent
            self.producer.close()
