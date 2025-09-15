import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from .json_helpers import create_kafka_message, deserialize_json, serialize_json
from ..config import kafka_config

logger = logging.getLogger(__name__)


class KafkaProducerAsync:
    """
    Async Kafka Producer
    For sending messages with async/await
    """

    def __init__(self, bootstrap_servers: str = None, **config):
        """
        Create async Producer

        Args:
            bootstrap_servers: Kafka servers address
            **config: Extra settings
        """
        self.bootstrap_servers = bootstrap_servers or kafka_config.bootstrap_servers

        self._default_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "value_serializer": lambda x: serialize_json(x).encode("utf-8"),
            "key_serializer": lambda x: x.encode("utf-8") if x else None,
            "acks": "all",
        }
        self._default_config.update(config)
        logger.debug(f"Producer config: {self._default_config}")
        self.producer = AIOKafkaProducer(**self._default_config)
        logger.debug("Producer created")

        self.is_started = False
        logger.info("Async Kafka Producer created")

    async def start(self):
        """Start the Producer"""
        logger.debug("Starting producer...")
        if not self.is_started:
            try:
                await self.producer.start()
                logger.debug("Producer started")
                self.is_started = True
                logger.info("Async Kafka Producer started")
            except KafkaError as e:
                logger.error(f"No Kafka brokers available: {e}")
                raise
            except Exception as e:
                logger.error(f"Failed to start Async Producer: {e}")
                raise

    async def stop(self):
        """Stop the Producer"""
        if self.is_started:
            try:
                await self.producer.stop()
                self.is_started = False
                logger.info("Async Kafka Producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Async Producer: {e}")

    def get_config(self):
        return self._default_config

    async def send_message(
        self, topic: str, message: Any, key: Optional[str] = None
    ) -> bool:
        """
        Send single message (async)

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

            # Send async
            await self.producer.send_and_wait(topic, value=kafka_message, key=key)

            logger.info(f"Message sent to '{topic}': {kafka_message['message_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to '{topic}': {e}")
            return False

    async def send_batch(
        self, topic: str, messages: List[Any], keys: Optional[List[str]] = None
    ) -> int:
        """
        Send multiple messages (async)

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

        # Send in parallel
        tasks = []
        for i, message in enumerate(messages):
            key = keys[i] if keys and i < len(keys) else None
            task = self.send_message(topic, message, key)
            tasks.append(task)

        # Wait for all sends
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes
        for result in results:
            if result is True:
                successful_sends += 1

        logger.info(
            f"Async batch send: {successful_sends}/{len(messages)} messages sent to '{topic}'"
        )
        return successful_sends


class KafkaConsumerAsync:
    """
    Async Kafka Consumer
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
        Create async Consumer

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
        }
        default_config.update(config)

        self.consumer = AIOKafkaConsumer(*topics, **default_config)
        self.is_started = False
        logger.info(f"Async Kafka Consumer created for topics: {topics}")

    async def start(self):
        """Start the Consumer"""
        if not self.is_started:
            try:
                await self.consumer.start()
                self.is_started = True
                self.last_check_time = datetime.now()
                logger.info("Async Kafka Consumer started")
            except Exception as e:
                logger.error(f"Failed to start Async Consumer: {e}")
                raise

    async def stop(self):
        """Stop the Consumer"""
        if self.is_started:
            try:
                await self.consumer.stop()
                self.is_started = False
                logger.info("Async Kafka Consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping Async Consumer: {e}")

    async def listen_forever(
        self,
        message_handler: Callable[[Dict], bool],
        max_messages: Optional[int] = None,
    ) -> int:
        """
        Listen forever for messages with callback function (async)

        Args:
            message_handler: Async function to handle messages
            max_messages: Max number of messages (None = infinite)

        Returns:
            Number of messages processed successfully
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return 0

        processed_count = 0
        logger.info("Starting async continuous listening...")

        try:
            async for message in self.consumer:
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

                    # Call handler async
                    if asyncio.iscoroutinefunction(message_handler):
                        success = await message_handler(message_data)
                    else:
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
            logger.error(f"Error in async listen_forever: {e}")

        logger.info(f"Processed {processed_count} messages")
        return processed_count

    async def get_new_messages(self, timeout_seconds: int = 5) -> List[Dict]:
        """
        Read all new messages since last time (async)

        Args:
            timeout_seconds: Max wait time

        Returns:
            List of new messages
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return []

        new_messages = []
        logger.info("Checking for new messages (async)...")

        try:
            # Check messages with timeout
            end_time = asyncio.get_event_loop().time() + timeout_seconds

            while asyncio.get_event_loop().time() < end_time:
                try:
                    # Wait for message with short timeout
                    message = await asyncio.wait_for(
                        self.consumer.__anext__(), timeout=1.0
                    )

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

                except asyncio.TimeoutError:
                    # No new messages, continue checking
                    continue
                except StopAsyncIteration:
                    # No more messages
                    break

            # Update last check time
            self.last_check_time = datetime.now()

        except Exception as e:
            logger.error(f"Error getting new messages (async): {e}")

        logger.info(f"Retrieved {len(new_messages)} new messages")
        return new_messages

    async def consume(self):
        """
        Consume messages (async) - generator that returns one message at a time
        Use with: async for message in consumer.consume():

        Yields:
            Dictionary with topic, key, value
        """
        if not self.is_started:
            logger.error("Consumer is not started. Call start() first.")
            return

        try:
            async for message in self.consumer:
                logger.debug(f"Received message from '{message}")
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
            logger.error(f"Error in async consume: {e}")
            return
