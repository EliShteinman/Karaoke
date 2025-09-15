# YouTube Service - משימות והסבר

## תפקיד הסרוביס
מטפל בכל הלוגיקה הקשורה ל-YouTube: חיפוש שירים והורדת קבצי אודיו. השירות יוצר את המסמך הראשוני ב-Elasticsearch, מוריד קבצים מ-YouTube, ומתזמן את תהליך העיבוד באמצעות Kafka.

## תזרים עבודה מפורט (Workflow)

### 1. פונקציה: חיפוש שירים ביוטיוב
1. **קבלת בקשת חיפוש** מ-API Server (HTTP call פנימי)
2. **שליחת שאילתה** ל-YouTube Data API v3
3. **עיבוד תוצאות** מה-API ופילטור לוידאו בלבד
4. **החזרת רשימה** של 10 תוצאות עם מטאדאטה מלאה

### 2. פונקציה: הורדת שיר נבחר
1. **קבלת בקשת הורדה** מ-API Server (HTTP call פנימי)
2. **יצירת מסמך ראשוני** ב-Elasticsearch עם מטאדאטה
3. **הורדת הקובץ** באמצעות YTDLP:
   - יצירת תיקייה: `/shared/audio/{video_id}/`
   - הורדה בפורמט MP3 באיכות 128kbps
   - שמירה כ-`original.mp3`
4. **עדכון Elasticsearch** עם נתיב הקובץ המקורי ומטאדאטה
5. **שליחת 3 הודעות Kafka (רק video_id):**
   - אירוע סיום: `song.downloaded`
   - פקודת עיבוד: `audio.process.requested`
   - פקודת תמלול: `transcription.process.requested`

## תקשורת עם שירותים אחרים

### עם API Server
- **מקבל:** בקשות חיפוש דרך HTTP (פנימי)
- **שולח:** תוצאות חיפוש (JSON)

### עם YouTube API
- **שולח:** שאילתות חיפוש עם מפתח API
- **מקבל:** מטאדאטה של וידאו (JSON)

### עם YTDLP
- **שולח:** פקודות הורדה עם אפשרויות מותאמות
- **מקבל:** קבצי אודיו מהורדים

### עם Kafka
- **שולח בלבד:** טופיקים `song.downloaded`, `audio.process.requested`, `transcription.process.requested` (producer)
- **לא מאזין לאף טופיק**

### עם Elasticsearch
- **יוצר:** מסמכי שירים חדשים (מקור האמת למטאדאטה)
- **מעדכן:** מסמכים עם נתיבי קבצים ומטאדאטה
- **לא קורא:** מידע (רק כותב/מעדכן/יוצר)

### עם Shared Storage
- **כותב:** קבצי אודיו מקוריים לנתיב `/shared/audio/{video_id}/original.mp3`
- **לא קורא:** קבצים (רק כותב)

## רשימת משימות פיתוח

### Phase 1: תשתית YouTube API
- [ ] הקמת פרויקט Python עם מבנה תיקיות נכון
- [ ] הגדרת YouTube Data API v3 client
- [ ] יישום פונקציית חיפוש בסיסית
- [ ] ולידציה ועיבוד תוצאות חיפוש
- [ ] הגדרת rate limiting למניעת חריגה מגבולות API

### Phase 2: אינטגרציה עם YTDLP
- [ ] הקמת YTDLP עם הגדרות מותאמות
- [ ] יישום לוגיקת הורדה עם error handling
- [ ] ניהול תיקיות ונתיבי קבצים
- [ ] וידוא איכות ופורמט קבצים מהורדים
- [ ] הוספת progress tracking להורדות

### Phase 3: יצירת מסמכים ב-Elasticsearch
- [ ] הקמת Elasticsearch client ליצירה ועדכונים
- [ ] **יישום יצירת מסמך ראשוני לפני הורדה**
- [ ] יישום עדכון מסמכים (partial updates)
- [ ] ניהול שגיאות כתיבה ל-Elasticsearch
- [ ] הוספת retry mechanism לעדכונים
- [ ] וידוא consistency בין מצב הקובץ למסמך

### Phase 4: תקשורת Kafka (producer בלבד)
- [ ] יישום Kafka producer לשליחת אירועים ופקודות
- [ ] **הגדרת שליחת video_id בלבד (ללא נתיבים)**
- [ ] הגדרת serialization/deserialization של הודעות
- [ ] טיפול בשגיאות תקשורת עם Kafka
- [ ] הוספת idempotency למניעת עיבוד כפול

### Phase 5: HTTP API לחיפוש והורדה
- [ ] הקמת FastAPI/Flask server פנימי
- [ ] יישום endpoint לחיפוש שירים
- [ ] יישום endpoint להורדת שירים
- [ ] אינטגרציה עם API Server
- [ ] הוספת caching לתוצאות חיפוש נפוצות
- [ ] ניהול שגיאות ו-timeouts

### Phase 6: שגיאות ואמינות
- [ ] ניהול מקיף של שגיאות YouTube API
- [ ] retry logic להורדות כושלות
- [ ] cleanup של קבצים חלקיים במקרה של שגיאה
- [ ] ניטור ו-alerting למצבי כשל
- [ ] הוספת circuit breaker pattern

### Phase 7: ביצועים ומעקב
- [ ] אופטימיזציה של הורדות מקבילות
- [ ] הוספת metrics ו-monitoring
- [ ] logging מפורט של כל שלבי התהליך
- [ ] health checks ו-status endpoints
- [ ] תיעוד ביצועים וגבולות מערכת

## דרישות טכניות

### תלויות עיקריות
- **google-api-python-client**: YouTube Data API
- **yt-dlp**: הורדת וידאו ואודיו מיוטיוב
- **kafka-python**: תקשורת עם Kafka
- **elasticsearch**: עדכון מסמכים
- **ffmpeg**: עיבוד אודיו (תלות של YTDLP)
- **aiofiles**: קריאה אסינכרונית של קבצים

### משתני סביבה נדרשים
```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_API_SERVICE_NAME=youtube
YOUTUBE_API_VERSION=v3

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=youtube_service_group

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=songs

# Storage
SHARED_STORAGE_PATH=/shared/audio

# YTDLP
YTDLP_OUTPUT_TEMPLATE=/shared/audio/%(id)s/original.%(ext)s
YTDLP_AUDIO_FORMAT=mp3
YTDLP_AUDIO_QUALITY=128K

# Service
SERVICE_PORT=8001
SERVICE_HOST=0.0.0.0
```

### הגדרות YTDLP מתקדמות
```python
ytdl_opts = {
    'format': 'bestaudio[ext=mp3]/best[ext=mp4]/best',
    'outtmpl': '/shared/audio/%(id)s/original.%(ext)s',
    'extractaudio': True,
    'audioformat': 'mp3',
    'audioquality': '128K',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
    'no_warnings': False,
    'ignoreerrors': False,
    'continuedl': True,
    'noplaylist': True,
    'writesubtitles': False,
    'writeautomaticsub': False
}
```

### מבנה קבצים מומלץ
```
youtube-service/
├── app/
│   ├── main.py              # נקודת כניסה
│   ├── services/
│   │   ├── youtube_search.py    # חיפוש ביוטיוב
│   │   ├── youtube_download.py  # הורדה עם YTDLP
│   │   ├── kafka_producer.py    # שליחת הודעות
│   │   └── elasticsearch_updater.py
│   ├── consumers/
│   │   └── download_consumer.py # Kafka consumer
│   ├── models/
│   │   ├── youtube_models.py    # מודלי נתונים
│   │   └── kafka_messages.py    # סכמות הודעות
│   ├── config/
│   │   ├── settings.py          # הגדרות
│   │   ├── youtube_config.py    # מפתחות API
│   │   └── ytdlp_config.py      # הגדרות YTDLP
│   └── utils/
│       ├── logger.py
│       ├── file_utils.py
│       └── retry_utils.py
├── tests/
└── requirements.txt
```

### אבטחה ושמירת מפתחות
- **YouTube API Key**: משתנה סביבה מוצפן
- **Rate Limiting**: מעקב אחר מכסות API
- **Input Validation**: ולידציה של video_id ופרמטרים
- **Access Control**: הגבלת גישה לשירותים פנימיים בלבד