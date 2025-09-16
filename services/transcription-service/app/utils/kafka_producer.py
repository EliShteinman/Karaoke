import json
import os
from kafka import KafkaProducer

class KafkaProducerManager:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BROKER"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks='all', # Ensure messages are received by all replicas
            retries=3,   # Retry sending messages on failure
        )

    def send_message(self, topic: str, message: dict):
        try:
            self.producer.send(topic, message)
            # self.producer.flush() # Flushing on every message can be slow. Consider flushing in batches or on close.
        except Exception as e:
            # Basic logging, a real logger would be better
            print(f"ERROR: Could not send message to Kafka topic '{topic}'. Reason: {e}")

    def close(self):
        self.producer.flush() # Ensure all buffered messages are sent
        self.producer.close()
