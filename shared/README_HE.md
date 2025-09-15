# מחלקת Shared - פרויקט קריוקי עברי

מחלקה זו מכילה את כל הקוד המשותף בין השירותים השונים של פרויקט הקריוקי העברי.

## 📁 מבנה התיקיות

```
shared/
├── kafka/          # לקוחות Kafka (אסינכרוני וסינכרוני)
├── elasticsearch/  # לקוחות Elasticsearch וניהול מסמכים
├── storage/        # ניהול קבצי אודיו ולירים
├── utils/          # כלים משותפים (לוגר וכו')
├── config.py       # ניהול קונפיגורציה מרכזי
├── README.md       # תיעוד באנגלית
├── README_HE.md    # תיעוד בעברית
├── CONFIGURATION.md # מדריך משתני סביבה (אנגלית)
└── CONFIGURATION_HE.md # מדריך משתני סביבה (עברית)
```

## 🎵 שימוש במערכת הקבצים

### יצירת מנהל קבצים

```python
from shared.storage import create_file_manager

# יצירת מנהל קבצים לvolume מקומי
file_manager = create_file_manager("volume", base_path="/shared")
```

### שמירת קבצים

```python
# שמירת אודיו מקורי
audio_path = file_manager.save_original_audio("video123", audio_bytes)

# שמירת אודיו ללא ווקאל
vocals_path = file_manager.save_vocals_removed_audio("video123", processed_audio)

# שמירת קובץ לירים
lyrics_path = file_manager.save_lyrics_file("video123", lrc_content)
```

### קריאת קבצים

```python
# קריאת אודיו
original_audio = file_manager.get_original_audio("video123")
vocals_removed = file_manager.get_vocals_removed_audio("video123")

# קריאת לירים כטקסט
lyrics = file_manager.get_lyrics("video123")
```

### בדיקות ויצירת חבילות

```python
# בדיקה אם השיר מוכן לקריוקי
if file_manager.is_song_ready_for_karaoke("video123"):
    # יצירת ZIP עם קבצים נדרשים
    zip_content = file_manager.create_karaoke_package("video123")

# מידע על קבצים
info = file_manager.get_song_files_info("video123")
```

## 📡 שימוש ב-Kafka

### Producer (שולח הודעות)

```python
from shared.kafka import KafkaProducerAsync, KafkaProducerSync

# אסינכרוני - ברירת מחדל localhost:9092
producer = KafkaProducerAsync()  # יתחבר ל-localhost:9092
# או לציין כתובת מותאמת:
# producer = KafkaProducerAsync("my-kafka-server:9092")

await producer.start()
await producer.send_message("my-topic", {"data": "value"}, key="optional_key")
await producer.stop()

# סינכרוני - ברירת מחדל localhost:9092
producer = KafkaProducerSync()  # יתחבר ל-localhost:9092
# או לציין כתובת מותאמת:
# producer = KafkaProducerSync("my-kafka-server:9092")

producer.start()
producer.send_message("my-topic", {"data": "value"}, key="optional_key")
producer.stop()
```

### Consumer (מקבל הודעות)

```python
from shared.kafka import KafkaConsumerAsync, KafkaConsumerSync

# אסינכרוני - האזנה תמידית
consumer = KafkaConsumerAsync(["my-topic"])  # ברירת מחדל localhost:9092
# או עם הגדרות מותאמות:
# consumer = KafkaConsumerAsync(["my-topic"], "my-kafka:9092", "my-group")

await consumer.start()

async def handle_message(message):
    print(f"Received: {message}")
    return True

await consumer.listen_forever(handle_message)
await consumer.stop()

# סינכרוני - קריאת הודעות חדשות
consumer = KafkaConsumerSync(["my-topic"])  # ברירת מחדל localhost:9092
consumer.start()
messages = consumer.get_new_messages(timeout_seconds=5)
consumer.stop()
```

### שליחת מספר הודעות

```python
# שליחה מקבילה (async)
count = await producer.send_batch("my-topic", [msg1, msg2, msg3])

# שליחה ברצף (sync)
count = producer.send_batch("my-topic", [msg1, msg2, msg3])
```

## 🔍 שימוש ב-Elasticsearch

### יצירת לקוח שירים

```python
from shared.elasticsearch import get_song_repository

# אסינכרוני (ברירת מחדל)
song_repo = get_song_repository(async_mode=True)

# סינכרוני
song_repo = get_song_repository(async_mode=False)
```

### פעולות על שירים

```python
# יצירת שיר חדש
song = await song_repo.create_song(
    video_id="video123",
    title="שם השיר",
    artist="שם האמן",
    channel="ערוץ יוטיוב",
    duration=180,
    thumbnail="http://...",
    search_text="מילות חיפוש"
)

# עדכון נתיב קובץ
await song_repo.update_file_path("video123", "vocals_removed", "/path/to/file")

# עדכון סטטוס
await song_repo.update_song_status("video123", "processing")

# סימון שגיאה
await song_repo.mark_song_failed("video123", "DOWNLOAD_FAILED", "שגיאה", "youtube_service")
```

### חיפוש ושאילתות

```python
# קבלת שירים מוכנים לקריוקי
ready_songs = await song_repo.get_ready_songs()

# חיפוש שירים לפי טקסט
results = await song_repo.search_songs("rick astley", limit=10, offset=0)

# שירים לפי סטטוס
downloading = await song_repo.get_songs_by_status("downloading")

# שירים שצריכים עיבוד
need_vocals = await song_repo.get_songs_for_processing("vocals_removed")
```

### הגדרות מתקדמות

```python
from shared.elasticsearch import elasticsearch_config, ElasticsearchFactory

# שינוי הגדרות
elasticsearch_config.songs_index = "my-songs-index"

# יצירת שירותים מותאמים
es_service = ElasticsearchFactory.create_elasticsearch_service("logs", async_mode=True)
```

## 📝 שימוש בלוגר

```python
from shared.utils import Logger

# קבלת לוגר
logger = Logger.get_logger(
    name="my-service",
    es_url="http://localhost:9200",
    index="logs",
    level=logging.INFO
)

# כתיבת לוגים (נשלח גם לקונסול וגם לElasticsearch)
logger.info("שירות התחיל")
logger.error("שגיאה במהלך עיבוד")
logger.debug("מידע debug")
```

## ⚙️ משתני סביבה

### Kafka
```bash
# אין משתני סביבה נדרשים - כתובת ברירת מחדל: localhost:9092
```

### Elasticsearch
```bash
ELASTICSEARCH_SCHEME=http
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=user
ELASTICSEARCH_PASSWORD=pass
ELASTICSEARCH_SONGS_INDEX=songs
ELASTICSEARCH_LOGS_INDEX=logs
```

### אחסון קבצים
```bash
# נתיב בסיס לvolume (ברירת מחדל: /shared)
FILE_STORAGE_BASE_PATH=/shared
```

## 🏗️ דוגמה מלאה - שירות עיבוד אודיו

```python
import asyncio
from shared.kafka import KafkaConsumerAsync, KafkaProducerAsync
from shared.elasticsearch import get_song_repository
from shared.storage import create_file_manager
from shared.utils import Logger

async def audio_processing_service():
    # יצירת רכיבים
    consumer = KafkaConsumerAsync(["audio.process.requested"], group_id="audio-service")
    producer = KafkaProducerAsync()
    song_repo = get_song_repository()
    file_manager = create_file_manager()
    logger = Logger.get_logger("audio-service")

    # התחלה
    await consumer.start()
    await producer.start()

    async def process_audio_message(message):
        try:
            video_id = message["value"]["video_id"]
            logger.info(f"Processing audio for {video_id}")

            # קריאת אודיו מקורי
            original_audio = file_manager.get_original_audio(video_id)

            # עיבוד הסרת ווקאל (קוד דמה)
            processed_audio = remove_vocals(original_audio)

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

            return True

        except Exception as e:
            logger.error(f"Failed to process audio: {e}")
            await song_repo.mark_song_failed(video_id, "AUDIO_PROCESSING_FAILED", str(e), "audio-service")
            return False

    # האזנה להודעות
    await consumer.listen_forever(process_audio_message)

# הרצה
if __name__ == "__main__":
    asyncio.run(audio_processing_service())
```

## 📚 הערות חשובות

- **אסינכרוני vs סינכרוני**: ברירת המחדל היא אסינכרוני. השתמש בסינכרוני רק אם צריך
- **מפינג Elasticsearch**: המפינג לשירים קבוע ומותאם לפרויקט הקריוקי
- **ניהול חיבורים**: תמיד קרא ל-`start()` ו-`stop()` ללקוחות Kafka
- **טיפול בשגיאות**: השתמש ב-`mark_song_failed()` לדיווח שגיאות
- **לוגר**: הלוגר שולח אוטומטית גם לקונסול וגם ל-Elasticsearch