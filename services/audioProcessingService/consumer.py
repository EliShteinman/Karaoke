from shared.kafka.sync_client import KafkaConsumerSync
from typing import Generator


def get_video_ids_from_kafka(topics:list[str], bootstrap_servers:str, group_id:str) -> Generator[str, None, None]:
    """
    Consumer that listens to Kafka and yields the video_id from each message.
    This function acts as a generator.
    """
    try:
        # יצירת מופע של הצרכן הסינכרוני
        consumer = KafkaConsumerSync(
            topics=topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id
        )
        # התחלת פעולת הצרכן
        consumer.start()

        # לולאת האזנה רציפה
        while True:
            # Process received messages and yield each video_id
            for message in consumer.consume():

                if 'video_id' in message["value"]:
                    video_id = message["value"]['video_id']
                    # מחזיר את ה-ID ומשהה את הפונקציה עד לקריאה הבאה
                    yield video_id
    except KeyboardInterrupt:
        print("Consumer was interrupted. Shutting down gracefully.")
    except Exception as e:
        print(f"A critical error occurred: {e}")

