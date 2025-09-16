# מחלקת Shared - פרויקט קריוקי עברי

מחלקה זו מכילה כלי תשתית גנריים ולוגיקה עסקית ספציפית לפרויקט הקריוקי העברי.

## 🏗️ ארכיטקטורה חדשה (לאחר רפקטורינג)

ספריית הshared אורגנה מחדש עם הפרדת אחריות נכונה:

### 📁 מבנה התיקיות

```
shared/
├── kafka/          # לקוחות Kafka גנריים (שכבת תשתית)
├── elasticsearch/  # שירותי Elasticsearch גנריים (שכבת תשתית)
├── storage/        # כלי אחסון קבצים גנריים (שכבת תשתית)
├── utils/          # כלים עזר גנריים (שכבת תשתית)
├── repositories/   # לוגיקה עסקית ספציפית לפרויקט (SongRepository)
├── README.md       # תיעוד באנגלית
└── README_HE.md    # התיעוד הזה
```

## 🎵 שימוש במערכת הקבצים (תשתית גנרית)

מערכת הקבצים תומכת בסוגי אחסון שונים: Volume Docker ותיקיה מקומית במחשב.

### יצירת מנהל קבצים - דוגמאות שונות

#### Volume Docker (בסביבת פיתוח וייצור)
```python
from shared.storage import create_file_manager

# יצירת מנהל קבצים עם Volume Docker
file_manager = create_file_manager("volume", base_path="/shared")

# דוגמה עם נתיב מותאם אישית
file_manager = create_file_manager("volume", base_path="/app/data")
```

#### תיקיה מקומית במחשב (בפיתוח מקומי)
```python
from shared.storage import create_file_manager

# תיקיה מקומית בבית המשתמש
file_manager = create_file_manager("local", base_path="/home/user/karaoke_files")

# תיקיה במחשב Windows
file_manager = create_file_manager("local", base_path="C:\\karaoke_files")

# תיקיה במחשב Mac
file_manager = create_file_manager("local", base_path="/Users/username/Documents/karaoke")
```

### שמירה וקריאת קבצים - דוגמאות מעשיות

#### דוגמה מלאה - עבודה עם קבצי אודיו
```python
from shared.storage import create_file_manager

def audio_processing_example():
    # יצירת מנהל קבצים
    file_manager = create_file_manager("volume", base_path="/shared")

    video_id = "ABC123XYZ"

    # נתוני דמה
    audio_data = b"binary_audio_data_here"  # נתוני אודיו בינאריים

    # שמירת אודיו מקורי
    try:
        audio_path = file_manager.save_original_audio(video_id, audio_data)
        print(f"אודיו נשמר ב: {audio_path}")

        # בדיקה שהקובץ נשמר בהצלחה
        saved_audio = file_manager.get_original_audio(video_id)
        if saved_audio:
            print("אודיו נטען בהצלחה מהאחסון")

        # עיבוד אודיו (דמה)
        processed_audio = saved_audio + b"_processed"

        # שמירת אודיו מעובד
        vocals_path = file_manager.save_vocals_removed_audio(video_id, processed_audio)
        print(f"אודיו מעובד נשמר ב: {vocals_path}")

    except Exception as e:
        print(f"שגיאה בעיבוד אודיו: {e}")

# הרצה
if __name__ == "__main__":
    audio_processing_example()
```

#### דוגמה - עבודה עם קבצי לירים
```python
from shared.storage import create_file_manager

def lyrics_example():
    file_manager = create_file_manager("local", base_path="/tmp/karaoke")

    video_id = "XYZ789"

    # שמירת לירים
    lyrics_content = """[00:12.00]שורה ראשונה
[00:15.50]שורה שנייה
[00:20.00]שורה שלישית"""

    lyrics_path = file_manager.save_lyrics_file(video_id, lyrics_content)
    print(f"לירים נשמרו ב: {lyrics_path}")

    # קריאת לירים
    saved_lyrics = file_manager.get_lyrics(video_id)
    if saved_lyrics:
        print("תוכן הלירים:")
        print(saved_lyrics)

if __name__ == "__main__":
    lyrics_example()
```

#### דוגמה - בדיקת מוכנות לקריוקי
```python
from shared.storage import create_file_manager

def karaoke_readiness_check():
    file_manager = create_file_manager("volume", base_path="/shared")

    video_id = "READY123"

    # בדיקה אם השיר מוכן לקריוקי
    if file_manager.is_song_ready_for_karaoke(video_id):
        print("השיר מוכן לקריוקי!")

        # יצירת חבילת קריוקי
        karaoke_zip = file_manager.create_karaoke_package(video_id)
        print(f"חבילת קריוקי נוצרה: {len(karaoke_zip)} bytes")

        # מידע על קבצי השיר
        files_info = file_manager.get_song_files_info(video_id)
        print("מידע על קבצים:")
        for file_type, exists in files_info.items():
            status = "✅ קיים" if exists else "❌ חסר"
            print(f"  {file_type}: {status}")
    else:
        print("השיר עדיין לא מוכן לקריוקי")

if __name__ == "__main__":
    karaoke_readiness_check()
```

## 📡 שימוש ב-Kafka (תשתית גנרית)

### Producer (שולח הודעות)

#### אסינכרוני
```python
import asyncio
from shared.kafka import KafkaProducerAsync

async def producer_example():
    producer = KafkaProducerAsync(bootstrap_servers="localhost:9092")

    await producer.start()

    # שליחת הודעה
    await producer.send_message("my-topic", {"data": "value"}, key="optional_key")

    await producer.stop()

# הרצה
if __name__ == "__main__":
    asyncio.run(producer_example())
```

#### סינכרוני
```python
from shared.kafka import KafkaProducerSync

def sync_producer_example():
    producer = KafkaProducerSync(bootstrap_servers="localhost:9092")

    producer.start()

    # שליחת הודעה
    producer.send_message("my-topic", {"data": "value"}, key="optional_key")

    producer.stop()

if __name__ == "__main__":
    sync_producer_example()
```

### Consumer (מקבל הודעות)

#### אסינכרוני
```python
import asyncio
from shared.kafka import KafkaConsumerAsync

async def consumer_example():
    consumer = KafkaConsumerAsync(
        topics=["my-topic"],
        bootstrap_servers="localhost:9092",
        group_id="my-group"
    )

    await consumer.start()

    async def handle_message(message):
        print(f"התקבל: {message}")
        return True

    # האזנה להודעות (זה ירוץ לעד)
    await consumer.listen_forever(handle_message)

if __name__ == "__main__":
    asyncio.run(consumer_example())
```

#### סינכרוני
```python
from shared.kafka import KafkaConsumerSync

def sync_consumer_example():
    consumer = KafkaConsumerSync(
        topics=["my-topic"],
        bootstrap_servers="localhost:9092",
        group_id="my-group"
    )

    consumer.start()

    def handle_message(message):
        print(f"התקבל: {message}")
        return True

    # האזנה להודעות
    consumer.listen_forever(handle_message)

if __name__ == "__main__":
    sync_consumer_example()
```

## 🔍 שימוש ב-Elasticsearch (תשתית + לוגיקה עסקית)

### שימוש ב-Factory גנרי של Elasticsearch

```python
from shared.elasticsearch import ElasticsearchFactory

# יצירת שירות עם פרמטרים מפורשים
es_service = ElasticsearchFactory.create_elasticsearch_service(
    index_name="logs",
    elasticsearch_host="localhost",
    elasticsearch_port=9200,
    elasticsearch_scheme="http",
    async_mode=True
)

# שירות עם אימות
es_service_auth = ElasticsearchFactory.create_elasticsearch_service(
    index_name="secure_logs",
    elasticsearch_host="es-cluster.example.com",
    elasticsearch_port=9200,
    elasticsearch_scheme="https",
    elasticsearch_username="user",
    elasticsearch_password="password",
    async_mode=True
)
```

### שימוש ב-Repositories ספציפיים לפרויקט

```python
from shared.repositories import RepositoryFactory

# יצירת song repository עם פרמטרים מפורשים
song_repo = RepositoryFactory.create_song_repository_from_params(
    elasticsearch_host="localhost",
    elasticsearch_port=9200,
    elasticsearch_scheme="http",
    songs_index="songs",
    async_mode=True
)

# עם אימות
secure_song_repo = RepositoryFactory.create_song_repository_from_params(
    elasticsearch_host="secure-es.example.com",
    elasticsearch_port=9200,
    elasticsearch_scheme="https",
    elasticsearch_username="app_user",
    elasticsearch_password="app_password",
    songs_index="production_songs",
    async_mode=True
)
```

### פעולות על שירים (לוגיקה עסקית)

```python
import asyncio
from shared.repositories import RepositoryFactory

async def song_operations_example():
    # יצירת repository
    song_repo = RepositoryFactory.create_song_repository_from_params(
        elasticsearch_host="localhost",
        elasticsearch_port=9200,
        songs_index="songs",
        async_mode=True
    )

    # יצירת שיר חדש
    song = await song_repo.create_song(
        video_id="video123",
        title="שם השיר",
        artist="שם האמן",
        channel="ערוץ יוטיוב",
        duration=180,
        thumbnail="http://example.com/thumb.jpg",
        search_text="מילות חיפוש"
    )

    # פעולות עדכון
    await song_repo.update_file_path("video123", "vocals_removed", "/path/to/file")
    await song_repo.update_song_status("video123", "processing")

    # חיפוש ושאילתות
    ready_songs = await song_repo.get_ready_songs()
    results = await song_repo.search_songs("rick astley", limit=10, offset=0)
    downloading = await song_repo.get_songs_by_status("downloading")

if __name__ == "__main__":
    asyncio.run(song_operations_example())
```

## 📝 שימוש בלוגר (תשתית גנרית)

```python
import logging
from shared.utils import Logger

def logger_example():
    # קבלת לוגר עם פרמטרים מפורשים
    logger = Logger.get_logger(
        name="my-service",
        es_url="http://localhost:9200",
        index="logs",
        level=logging.INFO
    )

    # לוגר עם Elasticsearch מאובטח
    secure_logger = Logger.get_logger(
        name="secure-service",
        es_url="https://user:password@es-cluster.example.com:9200",
        index="secure_logs",
        level=logging.DEBUG
    )

    # כתיבת לוגים
    logger.info("שירות התחיל")
    logger.error("שגיאה במהלך עיבוד")

    # לוגר מקומי בלבד (ללא Elasticsearch)
    local_logger = Logger.get_logger(name="local-service")
    local_logger.info("לוג מקומי בלבד")

if __name__ == "__main__":
    logger_example()
```

## 🏗️ דוגמה מלאה - שירות עיבוד אודיו

```python
import asyncio
import logging
from shared.kafka import KafkaConsumerAsync, KafkaProducerAsync
from shared.repositories import RepositoryFactory
from shared.storage import create_file_manager
from shared.utils import Logger

async def complete_audio_service_example():
    # הגדרת פרמטרים (בדרך כלל יגיעו מקונפיגורציה)
    kafka_servers = "localhost:9092"
    es_host = "localhost"
    es_port = 9200
    storage_path = "/shared"

    # יצירת רכיבים
    consumer = KafkaConsumerAsync(
        topics=["audio.process.requested"],
        bootstrap_servers=kafka_servers,
        group_id="audio-service"
    )

    producer = KafkaProducerAsync(bootstrap_servers=kafka_servers)

    song_repo = RepositoryFactory.create_song_repository_from_params(
        elasticsearch_host=es_host,
        elasticsearch_port=es_port,
        songs_index="songs",
        async_mode=True
    )

    file_manager = create_file_manager("volume", base_path=storage_path)
    logger = Logger.get_logger("audio-service")

    # התחלת שירותים
    await consumer.start()
    await producer.start()

    async def process_audio_message(message):
        try:
            video_id = message["value"]["video_id"]
            logger.info(f"עיבוד אודיו עבור {video_id}")

            # קריאת אודיו מקורי
            original_audio = file_manager.get_original_audio(video_id)
            if not original_audio:
                logger.error(f"לא נמצא אודיו מקורי עבור {video_id}")
                return False

            # עיבוד הסרת ווקאל (דמה)
            processed_audio = original_audio + b"_vocals_removed"

            # שמירת תוצאה
            path = file_manager.save_vocals_removed_audio(video_id, processed_audio)

            # עדכון Elasticsearch
            await song_repo.update_file_path(video_id, "vocals_removed", path)

            # שליחת הודעת סיום
            await producer.send_message("audio.vocals_processed", {
                "video_id": video_id,
                "status": "vocals_processed",
                "path": path
            })

            logger.info(f"עיבוד אודיו הושלם עבור {video_id}")
            return True

        except Exception as e:
            logger.error(f"נכשל עיבוד אודיו: {e}")
            await song_repo.mark_song_failed(video_id, "AUDIO_PROCESSING_FAILED", str(e), "audio-service")
            return False

    # האזנה להודעות
    logger.info("שירות עיבוד אודיו התחיל")
    await consumer.listen_forever(process_audio_message)

# הרצה
if __name__ == "__main__":
    asyncio.run(complete_audio_service_example())
```

## 📚 הערות חשובות

- **עצמאות**: כל כלי עובד באופן עצמאי עם פרמטרים מפורשים
- **גמישות**: ניתן להשתמש בכלים עם כל מערכת קונפיגורציה
- **בידוד**: כלי התשתית לא תלויים בקונפיגורציה ספציפית
- **שימוש חוזר**: ניתן להשתמש בכלים בפרויקטים שונים

## 🎯 מדריך מהיר

### דפוסי Import
```python
# כלי תשתית גנרית
from shared.storage import create_file_manager
from shared.kafka import KafkaProducerAsync, KafkaConsumerSync
from shared.elasticsearch import ElasticsearchFactory
from shared.utils import Logger

# לוגיקה עסקית ספציפית לפרויקט
from shared.repositories import RepositoryFactory
```

### עקרונות שימוש

1. **פרמטרים מפורשים**: כל כלי מקבל את הפרמטרים שלו במפורש
2. **אין תלויות קונפיגורציה**: הכלים לא יודעים מאיפה מגיעים הפרמטרים
3. **גמישות**: ניתן להשתמש עם כל מערכת קונפיגורציה או ללא כלל
4. **עצמאות**: כל כלי עובד בלי תלות בפרויקט ספציפי