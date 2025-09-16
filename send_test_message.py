import json
import os
from kafka import KafkaProducer

# --- הגדרות ---
# ודא שכתובת ה-broker נכונה. אם הגדרת אותה בקובץ .env, זה יעבוד.
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = "transcription.process.requested"

# ------------------------------------------------------------------
# !! חשוב !! שנה את הערך הזה ל-video_id אמיתי שיש לו קובץ אודיו
# ------------------------------------------------------------------
VIDEO_ID_TO_TEST = "YOUR_VIDEO_ID"


# ------------------------------------------------------------------


def send_kafka_message():
    """
    מתחבר לקafka ושולח הודעת בדיקה אחת.
    """
    print(f"Attempting to connect to Kafka broker at {KAFKA_BROKER}...")

    producer = None
    try:
        # יצירת ה-producer
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # ממיר את ההודעה ל-JSON
            acks='all',
            retries=3
        )
        print("✅ Successfully connected to Kafka.")

        # יצירת ההודעה
        message = {
            "video_id": VIDEO_ID_TO_TEST,
            "action": "transcribe"  # כפי שמוגדר בסכמה
        }

        print(f"Sending message to topic '{KAFKA_TOPIC}': {message}")

        # שליחת ההודעה
        future = producer.send(KAFKA_TOPIC, value=message)

        # המתנה לאישור שההודעה נשלחה
        record_metadata = future.get(timeout=10)
        print("✅ Message sent successfully!")
        print(f"  - Topic: {record_metadata.topic}")
        print(f"  - Partition: {record_metadata.partition}")
        print(f"  - Offset: {record_metadata.offset}")

    except Exception as e:
        print(f"❌ ERROR: Failed to send message to Kafka. Reason: {e}")

    finally:
        if producer:
            print("Flushing and closing Kafka producer...")
            producer.flush()  # מוודא שכל ההודעות נשלחו
            producer.close()
            print("Producer closed.")


if __name__ == "__main__":
    # טעינת משתני סביבה מקובץ .env (אם קיים)
    from dotenv import load_dotenv

    load_dotenv()

    if VIDEO_ID_TO_TEST == "YOUR_VIDEO_ID":
        print("\n⚠️  WARNING: Please change the 'VIDEO_ID_TO_TEST' variable in the script before running!\n")
    else:
        send_kafka_message()
