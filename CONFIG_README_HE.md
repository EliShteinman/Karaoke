# מדריך קונפיגורציה - פרויקט קריוקי עברי

מדריך מלא למערכת הקונפיגורציה המרכזית ב-`/config.py`.

## 🔧 איך הקונפיגורציה עובדת

מערכת הקונפיגורציה היא **מרכזית ומודולרית**. לכל שירות יש מחלקת קונפיגורציה עצמאית שמגדירה במפורש את כל משתני הסביבה שהוא צריך.

### עקרונות יסוד:
1. **עצמאות**: כל שירות רואה את כל הפרמטרים שהוא צריך במקום אחד
2. **מפורש**: אין תלויות נסתרות או קונפיגורציה גלובלית משותפת
3. **ברירות מחדל חכמות**: ברירות מחדל בטוחות לפיתוח, אימות נדרש להגדרות קריטיות
4. **כפילות במתכוון**: גם אם שירותים משתמשים באותה תשתית, כל אחד מגדיר את הפרמטרים שלו לבהירות

## 📋 מחלקות קונפיגורציה של שירותים

### איך כל שירות מייבא קונפיגורציה

```python
# בכל שירות - ייבוא הקונפיגורציה המרכזית
from config import config

# שירות יוטיוב
class YouTubeService:
    def __init__(self):
        # השירות מקבל רק את הקונפיגורציה שלו
        self.service_config = config.youtube_service

        # כל הפרמטרים זמינים בקונפיגורציה שלו
        self.api_key = self.service_config.api_key
        self.kafka_servers = self.service_config.kafka_bootstrap_servers
        self.es_host = self.service_config.elasticsearch_host

# שירות אודיו
class AudioService:
    def __init__(self):
        # השירות מקבל רק את הקונפיגורציה שלו
        self.service_config = config.audio_service

        # כל הפרמטרים זמינים בקונפיגורציה שלו
        self.kafka_servers = self.service_config.kafka_bootstrap_servers
        self.es_host = self.service_config.elasticsearch_host
        self.storage_path = self.service_config.storage_base_path

# שרת API
class APIServer:
    def __init__(self):
        # השירות מקבל רק את הקונפיגורציה שלו
        self.service_config = config.api_server

        # כל הפרמטרים זמינים בקונפיגורציה שלו
        self.host = self.service_config.host
        self.port = self.service_config.port
        self.kafka_servers = self.service_config.kafka_bootstrap_servers
```

## ⚙️ משתני סביבה לפי שירות

### שירות יוטיוב (`config.youtube_service`)

**הגדרות ספציפיות לשירות:**
```bash
YOUTUBE_API_KEY=your_api_key                    # נדרש - אין ברירת מחדל
YOUTUBE_MAX_RESULTS=10                          # אופציונלי
YOUTUBE_DOWNLOAD_QUALITY=bestaudio             # אופציונלי
YOUTUBE_DOWNLOAD_FORMAT=mp3                    # אופציונלי
```

**תלויות תשתית (מוגדרות במפורש עבור השירות הזה):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # אופציונלי - יש ברירת מחדל
KAFKA_CONSUMER_GROUP_YOUTUBE=youtube-service   # אופציונלי - יש ברירת מחדל
KAFKA_TOPIC_DOWNLOAD_REQUESTED=song.download.requested  # אופציונלי - יש ברירת מחדל
KAFKA_TOPIC_SONG_DOWNLOADED=song.downloaded    # אופציונלי - יש ברירת מחדל

ELASTICSEARCH_HOST=localhost                    # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_PORT=9200                         # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_SCHEME=http                       # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_USERNAME=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_PASSWORD=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_SONGS_INDEX=songs                # אופציונלי - יש ברירת מחדל

STORAGE_BASE_PATH=/shared                       # אופציונלי - יש ברירת מחדל
```

### שירות אודיו (`config.audio_service`)

**הגדרות ספציפיות לשירות:**
```bash
AUDIO_VOCAL_REMOVAL_METHOD=spleeter            # אופציונלי - יש ברירת מחדל
AUDIO_OUTPUT_FORMAT=mp3                        # אופציונלי - יש ברירת מחדל
AUDIO_SAMPLE_RATE=44100                        # אופציונלי - יש ברירת מחדל
AUDIO_BITRATE=128k                             # אופציונלי - יש ברירת מחדל
```

**תלויות תשתית (מוגדרות במפורש עבור השירות הזה):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # אופציונלי - יש ברירת מחדל
KAFKA_CONSUMER_GROUP_AUDIO=audio-service       # אופציונלי - יש ברירת מחדל
KAFKA_TOPIC_AUDIO_PROCESS_REQUESTED=audio.process.requested  # אופציונלי - יש ברירת מחדל
KAFKA_TOPIC_VOCALS_PROCESSED=audio.vocals_processed  # אופציונלי - יש ברירת מחדל

ELASTICSEARCH_HOST=localhost                    # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_PORT=9200                         # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_SCHEME=http                       # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_USERNAME=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_PASSWORD=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_SONGS_INDEX=songs                # אופציונלי - יש ברירת מחדל

STORAGE_BASE_PATH=/shared                       # אופציונלי - יש ברירת מחדל
```

### שרת API (`config.api_server`)

**הגדרות ספציפיות לשירות:**
```bash
API_HOST=0.0.0.0                               # אופציונלי - יש ברירת מחדל
API_PORT=8000                                  # אופציונלי - יש ברירת מחדל
API_DEBUG=false                                # אופציונלי - יש ברירת מחדל
API_CORS_ORIGINS=*                             # אופציונלי - יש ברירת מחדל
```

**תלויות תשתית (מוגדרות במפורש עבור השירות הזה):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # אופציונלי - יש ברירת מחדל

ELASTICSEARCH_HOST=localhost                    # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_PORT=9200                         # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_SCHEME=http                       # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_USERNAME=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_PASSWORD=                         # אופציונלי - אין ברירת מחדל (אימות)
```

### שירות תמלול (`config.transcription_service`)

**הגדרות ספציפיות לשירות:**
```bash
TRANSCRIPTION_MODEL_NAME=whisper-base          # אופציונלי - יש ברירת מחדל
TRANSCRIPTION_LANGUAGE=auto                    # אופציונלי - יש ברירת מחדל
TRANSCRIPTION_OUTPUT_FORMAT=lrc                # אופציונלי - יש ברירת מחדל
```

**תלויות תשתית (מוגדרות במפורש עבור השירות הזה):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # אופציונלי - יש ברירת מחדל
KAFKA_CONSUMER_GROUP_TRANSCRIPTION=transcription-service  # אופציונלי - יש ברירת מחדל
KAFKA_TOPIC_TRANSCRIPTION_REQUESTED=transcription.process.requested  # אופציונלי - יש ברירת מחדל
KAFKA_TOPIC_TRANSCRIPTION_DONE=transcription.done  # אופציונלי - יש ברירת מחדל

ELASTICSEARCH_HOST=localhost                    # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_PORT=9200                         # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_SCHEME=http                       # אופציונלי - יש ברירת מחדל
ELASTICSEARCH_USERNAME=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_PASSWORD=                         # אופציונלי - אין ברירת מחדל (אימות)
ELASTICSEARCH_SONGS_INDEX=songs                # אופציונלי - יש ברירת מחדל

STORAGE_BASE_PATH=/shared                       # אופציונלי - יש ברירת מחדל
```

### לקוח Streamlit (`config.streamlit_client`)

**הגדרות ספציפיות לשירות:**
```bash
STREAMLIT_TITLE=HebKaraoke                     # אופציונלי - יש ברירת מחדל
STREAMLIT_THEME=dark                           # אופציונלי - יש ברירת מחדל
STREAMLIT_API_BASE_URL=http://localhost:8000   # אופציונלי - יש ברירת מחדל
```

## 🏗️ הגדרות פרויקט גלובליות

**מטא-נתוני פרויקט:**
```bash
PROJECT_NAME=HebKaraoke                        # אופציונלי - יש ברירת מחדל
PROJECT_VERSION=1.0.0                         # אופציונלי - יש ברירת מחדל
ENVIRONMENT=development                        # אופציונלי - יש ברירת מחדל (development/production)
```

## 🔐 אבטחת קונפיגורציה

### משתנים נדרשים מול אופציונליים

**נדרש** (יזרוק שגיאה אם חסר):
- `YOUTUBE_API_KEY` - קריטי לתפקוד שירות יוטיוב

**אופציונלי** (יש ברירות מחדל בטוחות):
- כל הגדרות התשתית (כתובות, פורטים, וכו')
- כל הגדרות ספציפיות לשירותים

### אסטרטגיית ברירות מחדל חכמות

- **הגדרות תשתית**: ברירת מחדל לערכי פיתוח localhost
- **מפתחות API קריטיים**: אין ברירות מחדל - חייבים להינתן במפורש
- **הגדרות שירותים**: ברירות מחדל הגיוניות לשימוש טיפוסי

### קונפיגורציה ספציפית לסביבה

```python
from config import config

# בדיקת סביבה
if config.is_production():
    # לוגיקה ספציפית לייצור
    pass
elif config.is_development():
    # לוגיקה ספציפית לפיתוח
    pass
```

## 📚 דוגמאות קונפיגורציה

### סביבת פיתוח (.env)
```bash
# רק משתנים נדרשים
YOUTUBE_API_KEY=your_actual_api_key

# כל השאר משתמשים בברירות מחדל לפיתוח מקומי
```

### סביבת ייצור (.env)
```bash
# נדרש
YOUTUBE_API_KEY=your_production_api_key

# עקיפות תשתית
KAFKA_BOOTSTRAP_SERVERS=kafka-cluster:9092
ELASTICSEARCH_HOST=elastic-cluster
ELASTICSEARCH_USERNAME=production_user
ELASTICSEARCH_PASSWORD=production_password
STORAGE_BASE_PATH=/production/shared

# סביבה
ENVIRONMENT=production
```

### סביבת Docker Compose
```bash
# פורטים ספציפיים לשירות
API_PORT=8080
STREAMLIT_API_BASE_URL=http://api-server:8080

# כתובות צביר
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ELASTICSEARCH_HOST=elasticsearch
```

## 🎯 שיטות עבודה מומלצות

1. **בידוד שירותים**: כל שירות ניגש רק ל-`config.{service_name}`
2. **פרמטרים מפורשים**: העברת קונפיגורציה במפורש לכלים משותפים
3. **קבצי סביבה**: שימוש בקבצי `.env` להגדרות ספציפיות לסביבה
4. **אבטחה**: לעולם לא לבצע commit של מפתחות API או סיסמאות לבקרת גרסאות
5. **תיעוד**: עדכון המדריך הזה בעת הוספת אפשרויות קונפיגורציה חדשות

## 🚀 שימוש בשירותים

```python
# services/youtube-service/main.py
from config import config
from shared.kafka import KafkaProducerAsync
from shared.repositories import RepositoryFactory

def main():
    # קבלת קונפיגורציית שירות
    service_config = config.youtube_service

    # יצירת רכיבים עם קונפיגורציה מפורשת
    producer = KafkaProducerAsync(
        bootstrap_servers=service_config.kafka_bootstrap_servers
    )

    song_repo = RepositoryFactory.create_song_repository_from_config(
        service_config, async_mode=True
    )

    # לוגיקת שירות כאן...
```

גישה זו מבטיחה שלכל שירות יש נראות מלאה לכל הקונפיגורציה שהוא צריך תוך שמירה על הפרדה נקייה בין שירותים.