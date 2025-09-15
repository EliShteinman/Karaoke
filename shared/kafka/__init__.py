"""
Kafka client package for HebKaraoke
Provides both async and sync Kafka producers and consumers
"""

from .async_client import KafkaProducerAsync, KafkaConsumerAsync
from .sync_client import KafkaProducerSync, KafkaConsumerSync
from .json_helpers import serialize_json, deserialize_json, create_kafka_message

__all__ = [
    "KafkaProducerAsync",
    "KafkaConsumerAsync",
    "KafkaProducerSync",
    "KafkaConsumerSync",
    "serialize_json",
    "deserialize_json",
    "create_kafka_message"
]