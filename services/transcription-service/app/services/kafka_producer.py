from kafka import KafkaProducer
import json
import os

class KafkaProducerService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BROKER"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        self.topic = os.getenv("KAFKA_TOPIC_DONE")

    def send_result(self, message: dict):
        self.producer.send(self.topic, message)
        self.producer.flush()
