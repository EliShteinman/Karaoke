import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from .json_helpers import create_kafka_message, deserialize_json, serialize_json
from ..config import kafka_config

logger = logging.getLogger(__name__)


class KafkaProducerSync:
    """
    Sync Kafka Producer
    For sending messages with standard Python calls
    """

    def __init__(self, bootstrap_servers: str = None, **config):
        """
        Create sync Producer

        Args:
            bootstrap_servers: Kafka servers address
            **config: Extra settings
        """
        self.bootstrap_servers = bootstrap_servers or kafka_config.bootstrap_servers

        self._default_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "value_serializer": lambda x: serialize_json(x).encode("utf-8"),
            "key_serializer": lambda x: x.encode("utf-8") if x else None,
        }
        self._default_config.update(config)
        logger.debug(f"Producer config: {self._default_config}")
        self.producer = KafkaProducer(**self._default_config)
        logger.debug("Producer created")

        self.is_started = True
        logger.info("Sync Kafka Producer created")

    def start(self):
        """Start the Producer"""
        logger.debug("Starting producer...")
        if not self.is_started:
            try:
                # Sync producer starts immediately
                self.is_started = True
                logger.info("Sync Kafka Producer started")
            except KafkaError as e:
                logger.error(f"No Kafka brokers available: {e}")
                raise
            except Exception as e:
                logger.error(f"Failed to start Sync Producer: {e}")
                raise

    def stop(self):
        """Stop the Producer"""
        if self.is_started:
            try:
                self.producer.close()
                self.is_started = False
                logger.info("Sync Kafka Producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Sync Producer: {e}")

    def get_config(self):
        return self._default_config

    def send_message(
        self, topic: str, message: Any, key: Optional[str] = None
    ) -> bool:
        """
        Send single message (sync)

        Args:
            topic: Topic name
            message: Message to send
            key: Optional key

        Returns:
            True if message sent successfully
        """
        if not self.is_started:
            logger.error("Producer is not started. Call start() first.")
            return False

        try:
            # Create structured message
            kafka_message = create_kafka_message(topic, message, key)

            # Send sync
            future = self.producer.send(topic, value=kafka_message, key=key)
            record_metadata = future.get(timeout=10)  # Wait for confirmation

            logger.info(f"Message sent to '{topic}': {kafka_message['message_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to '{topic}': {e}")
            return False

    def send_batch(
        self, topic: str, messages: List[Any], keys: Optional[List[str]] = None
    ) -> int:
        """
        Send multiple messages (sync)

        Args:
            topic: Topic name
            messages: List of messages
            keys: List of keys (optional)

        Returns:
            Number of messages sent successfully
        """
        if not self.is_started:
            logger.error("Producer is not started. Call start() first.")
            return 0

        successful_sends = 0

        # Send sequentially
        for i, message in enumerate(messages):
            key = keys[i] if keys and i < len(keys) else None
            if self.send_message(topic, message, key):
                successful_sends += 1

        logger.info(
            f"Sync batch send: {successful_sends}/{len(messages)} messages sent to '{topic}'"
        )
        return successful_sends


class KafkaConsumerSync:
    """
    Sync Kafka Consumer
    With 2 main methods: listen forever and read updates
    """

    def __init__(
        self,
        topics: List[str],
        bootstrap_servers: str = None,
        group_id: str = "default_group",
        **config,
    ):
        """
        Create sync Consumer

        Args:
            topics: List of topics to follow
            bootstrap_servers: Kafka servers address
            group_id: Consumer group ID
            **config: Extra settings
        """
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers or kafka_config.bootstrap_servers
        self.group_id = group_id
        self.last_check_time = None

        default_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "group_id": group_id,
            "value_deserializer": lambda x: deserialize_json(x.decode("utf-8")),
            "key_deserializer": lambda x: x.decode("utf-8") if x else None,
            "auto_offset_reset": "latest",
            "consumer_timeout_ms": 1000,
        }
        default_config.update(config)

        self.consumer = KafkaConsumer(*topics, **default_config)
        self.is_started = False
        logger.info(f"Sync Kafka Consumer created for topics: {topics}")

    def start(self):
        """Start the Consumer"""
        if not self.is_started:
            try:
                # Sync consumer starts immediately
                self.is_started = True
                self.last_check_time = datetime.now()
                logger.info("Sync Kafka Consumer started")
            except Exception as e:
                logger.error(f"Failed to start Sync Consumer: {e}")
                raise

    def stop(self):
        """Stop the Consumer"""
        if self.is_started:
            try:
                self.consumer.close()
                self.is_started = False
                logger.info("Sync Kafka Consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping Sync Consumer: {e}")

    def listen_forever(
        self,
        message_handler: Callable[[Dict], bool],
        max_messages: Optional[int] = None,
    ) -> int:
        """
        Listen forever for messages with callback function (sync)

        Args:
            message_handler: Function to handle messages
            max_messages: Max number of messages (None = infinite)

        Returns:
            Number of messages processed successfully
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return 0

        processed_count = 0
        logger.info("Starting sync continuous listening...")

        try:
            for message in self.consumer:
                try:
                    # Process the message
                    message_data = {
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                        "key": message.key,
                        "value": message.value,
                        "timestamp": message.timestamp,
                        "received_at": datetime.now().isoformat(),
                    }

                    # Call handler
                    success = message_handler(message_data)

                    if success:
                        processed_count += 1
                        logger.debug(f"Processed message from '{message.topic}'")
                    else:
                        logger.warning(
                            f"Failed to process message from '{message.topic}'"
                        )

                    # Check message limit
                    if max_messages and processed_count >= max_messages:
                        logger.info(f"Reached max messages limit: {max_messages}")
                        break

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in sync listen_forever: {e}")

        logger.info(f"Processed {processed_count} messages")
        return processed_count

    def get_new_messages(self, timeout_seconds: int = 5) -> List[Dict]:
        """
        Read all new messages since last time (sync)

        Args:
            timeout_seconds: Max wait time

        Returns:
            List of new messages
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return []

        new_messages = []
        logger.info("Checking for new messages (sync)...")

        try:
            # Poll for messages with timeout
            message_batch = self.consumer.poll(timeout_ms=timeout_seconds * 1000)

            for topic_partition, messages in message_batch.items():
                for message in messages:
                    message_data = {
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                        "key": message.key,
                        "value": message.value,
                        "timestamp": message.timestamp,
                        "received_at": datetime.now().isoformat(),
                    }
                    new_messages.append(message_data)

            # Update last check time
            self.last_check_time = datetime.now()

        except Exception as e:
            logger.error(f"Error getting new messages (sync): {e}")

        logger.info(f"Retrieved {len(new_messages)} new messages")
        return new_messages

    def consume(self):
        """
        Consume messages (sync) - generator that returns one message at a time
        Use with: for message in consumer.consume():

        Yields:
            Dictionary with topic, key, value
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return

        try:
            for message in self.consumer:
                logger.debug(f"Received message from '{message.topic}'")
                yield {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "key": message.key,
                    "value": message.value,
                    "timestamp": message.timestamp,
                    "received_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error in sync consume: {e}")
            return