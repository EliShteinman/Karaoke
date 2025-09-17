# מדריך קונפיגורציה - פרויקט HebKaraoke

## ⚠️ חשוב להבין!

הקובץ `/config.py` הוא **תבנית המכילה את כל משתני הסביבה שכלי הספריות המשותפות דורשים** - לא קובץ קונפיגורציה אמיתי!

### מה הקובץ הזה מכיל:
- ✅ **כל המשתנים שספריית shared דורשת** מכל שירות
- ✅ **תיעוד מפורט** של כל משתנה ומה הוא עושה
- ✅ **תבנית להעתקה חובה** לכל שירות כשהוא מופרד
- ❌ **לא** קובץ שכולם משתמשים בו יחד

## 🔧 איך הקונפיגורציה עובדת

**כל שירות חייב ליצור קובץ קונפיגורציה משלו ולהעתיק את כל המשתנים הרלוונטיים!**

### עקרונות מפתח:
1. **העתקה חובה**: כל שירות חייב להעתיק את כל המשתנים שספריית shared דורשת ממנו
2. **עצמאות מלאה**: כל שירות יוצר קובץ קונפיגורציה משלו
3. **בסיס + תוספות**: משתנים מהתבנית הם בסיס חובה, השירות יכול להוסיף משתנים פנימיים
4. **אין ברירה**: אי אפשר לדלג על משתנים שספריית shared דורשת

## 🚀 איך כל שירות משתמש בקונפיגורציה

```python
# כל שירות יוצר קובץ config.py משלו
# services/youtube-service/config.py
import os

class Config:
    def __init__(self):
        # 🔴 חובה - כל המשתנים שספריית shared דורשת
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")

        # 🟢 תוספות - משתנים פנימיים של השירות
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is required for YouTube functionality")

# יצירת מופע קונפיגורציה
config = Config()
```

## ⚙️ משתני כלים חובה לפי שירות

בהתבסס על ההנחיות ארכיטקטוניות וספריית shared:

### API Server
**משתמש בכלים:** Elasticsearch (קריאה בלבד)

**🔴 משתנים חובה (נדרשים על ידי כלי shared):**
```bash
# הגדרות שרת
API_HOST=0.0.0.0                               # כתובת IP של השרת
API_PORT=8000                                  # פורט השרת
API_DEBUG=false                                # מצב דיבוג
API_CORS_ORIGINS=*                             # CORS origins מותרים

# חיבור Elasticsearch - נדרש על ידי כלי shared/elasticsearch
ELASTICSEARCH_HOST=localhost                    # כתובת שרת Elasticsearch
ELASTICSEARCH_PORT=9200                         # פורט Elasticsearch
ELASTICSEARCH_SCHEME=http                       # פרוטוקול
ELASTICSEARCH_USERNAME=                         # שם משתמש (אם נדרש אימות)
ELASTICSEARCH_PASSWORD=                         # סיסמה (אם נדרש אימות)
```

### YouTube Service
**משתמש בכלים:** Kafka, Elasticsearch, Storage

**🔴 משתנים חובה (נדרשים על ידי כלי shared):**
```bash
# חיבור Kafka - נדרש על ידי כלי shared/kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # רשימת שרתי Kafka
KAFKA_CONSUMER_GROUP_YOUTUBE=youtube-service   # קבוצת צרכנים
KAFKA_TOPIC_DOWNLOAD_REQUESTED=song.download.requested  # נושא בקשה
KAFKA_TOPIC_SONG_DOWNLOADED=song.downloaded    # נושא השלמה

# חיבור Elasticsearch - נדרש על ידי כלי shared/elasticsearch
ELASTICSEARCH_HOST=localhost                    # כתובת שרת Elasticsearch
ELASTICSEARCH_PORT=9200                         # פורט Elasticsearch
ELASTICSEARCH_SCHEME=http                       # פרוטוקול
ELASTICSEARCH_USERNAME=                         # שם משתמש (אם נדרש אימות)
ELASTICSEARCH_PASSWORD=                         # סיסמה (אם נדרש אימות)
ELASTICSEARCH_SONGS_INDEX=songs                # אינדקס השירים

# אחסון קבצים - נדרש על ידי כלי shared/storage
STORAGE_BASE_PATH=/shared                       # תיקיית בסיס לקבצים
```

**🟢 משתני שירות פנימיים (תוספות):**
```bash
# תוספות ספציפיות לשירות YouTube
YOUTUBE_API_KEY=your_api_key                    # מפתח API של YouTube
YOUTUBE_MAX_RESULTS=10                          # כמות תוצאות חיפוש
YOUTUBE_DOWNLOAD_QUALITY=bestaudio             # איכות הורדה
YOUTUBE_DOWNLOAD_FORMAT=wav                    # פורמט קובץ
```

### Audio Processing Service
**משתמש בכלים:** Kafka, Elasticsearch, Storage

**🔴 משתנים חובה (נדרשים על ידי כלי shared):**
```bash
# חיבור Kafka - נדרש על ידי כלי shared/kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # רשימת שרתי Kafka
KAFKA_CONSUMER_GROUP_AUDIO=audio-service       # קבוצת צרכנים
KAFKA_TOPIC_AUDIO_PROCESS_REQUESTED=audio.process.requested  # נושא בקשה
KAFKA_TOPIC_VOCALS_PROCESSED=audio.vocals_processed  # נושא השלמה

# חיבור Elasticsearch - נדרש על ידי כלי shared/elasticsearch
ELASTICSEARCH_HOST=localhost                    # כתובת שרת Elasticsearch
ELASTICSEARCH_PORT=9200                         # פורט Elasticsearch
ELASTICSEARCH_SCHEME=http                       # פרוטוקול
ELASTICSEARCH_USERNAME=                         # שם משתמש (אם נדרש אימות)
ELASTICSEARCH_PASSWORD=                         # סיסמה (אם נדרש אימות)
ELASTICSEARCH_SONGS_INDEX=songs                # אינדקס השירים

# אחסון קבצים - נדרש על ידי כלי shared/storage
STORAGE_BASE_PATH=/shared                       # תיקיית בסיס לקבצים
```

**🟢 משתני שירות פנימיים (תוספות):**
```bash
# תוספות ספציפיות לעיבוד אודיו
AUDIO_VOCAL_REMOVAL_METHOD=spleeter            # שיטת הסרת שירה
AUDIO_OUTPUT_FORMAT=wav                        # פורמט פלט
AUDIO_SAMPLE_RATE=44100                        # קצב דגימה
AUDIO_BITRATE=128k                             # איכות bitrate
```

### Transcription Service
**משתמש בכלים:** Kafka, Elasticsearch, Storage

**🔴 משתנים חובה (נדרשים על ידי כלי shared):**
```bash
# חיבור Kafka - נדרש על ידי כלי shared/kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # רשימת שרתי Kafka
KAFKA_CONSUMER_GROUP_TRANSCRIPTION=transcription-service  # קבוצת צרכנים
KAFKA_TOPIC_TRANSCRIPTION_REQUESTED=transcription.process.requested  # נושא בקשה
KAFKA_TOPIC_TRANSCRIPTION_DONE=transcription.done  # נושא השלמה

# חיבור Elasticsearch - נדרש על ידי כלי shared/elasticsearch
ELASTICSEARCH_HOST=localhost                    # כתובת שרת Elasticsearch
ELASTICSEARCH_PORT=9200                         # פורט Elasticsearch
ELASTICSEARCH_SCHEME=http                       # פרוטוקול
ELASTICSEARCH_USERNAME=                         # שם משתמש (אם נדרש אימות)
ELASTICSEARCH_PASSWORD=                         # סיסמה (אם נדרש אימות)
ELASTICSEARCH_SONGS_INDEX=songs                # אינדקס השירים

# אחסון קבצים - נדרש על ידי כלי shared/storage
STORAGE_BASE_PATH=/shared                       # תיקיית בסיס לקבצים
```

**🟢 משתני שירות פנימיים (תוספות):**
```bash
# תוספות ספציפיות לתמלול
TRANSCRIPTION_MODEL_NAME=whisper-base          # מודל זיהוי
TRANSCRIPTION_LANGUAGE=auto                    # שפת זיהוי
TRANSCRIPTION_OUTPUT_FORMAT=lrc                # פורמט פלט
```

### Streamlit Client
**משתמש בכלים:** חיבור HTTP ל-API Server

**🔴 משתנים חובה (נדרשים על ידי כלי shared):**
```bash
# חיבור API Server - נדרש על ידי כלי shared/http
STREAMLIT_API_BASE_URL=http://localhost:8000   # כתובת שרת API
```

**🟢 משתני שירות פנימיים (תוספות):**
```bash
# תוספות ספציפיות לממשק
STREAMLIT_TITLE=HebKaraoke                     # כותרת האפליקציה
STREAMLIT_THEME=dark                           # הגדרת נושא
```

## 📋 הוראות ליצירת קובץ קונפיגורציה לשירות

### 🚨 חובה לכל שירות!

כשמפרסים כל שירות בקונטיינרים נפרדים, **חובה** ליצור קובץ `config.py` נפרד לכל שירות.

### שלב 1: יצירת הקובץ
```bash
# יצירת קובץ קונפיגורציה בתיקיית השירות
touch services/youtube-service/config.py
```

### שלב 2: העתקה חובה של משתנים משותפים
**העתקת כל המשתנים הרלוונטיים מ-`/config.py` בדיוק כמו שהם:**

לדוגמה, עבור שירות YouTube:

```python
# services/youtube-service/config.py
import os

class Config:
    def __init__(self):
        # 🔴 חובה - העתקה מדויקת מהתבנית
        # כל המשתנים שספריית shared דורשת:

        # קונפיגורציית Kafka
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_YOUTUBE", "youtube-service")
        self.kafka_topic_download_requested = os.getenv("KAFKA_TOPIC_DOWNLOAD_REQUESTED", "song.download.requested")
        self.kafka_topic_song_downloaded = os.getenv("KAFKA_TOPIC_SONG_DOWNLOADED", "song.downloaded")

        # קונפיגורציית Elasticsearch
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        # קונפיגורציית אחסון
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")

        # 🟢 תוספות - משתני שירות פנימיים
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")

        self.max_results = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))
        self.download_quality = os.getenv("YOUTUBE_DOWNLOAD_QUALITY", "bestaudio")
        self.download_format = os.getenv("YOUTUBE_DOWNLOAD_FORMAT", "wav")

# יצירת מופע קונפיגורציה
config = Config()
```

### ✅ רשימת בדיקה לכל שירות:

1. **העתק את כל המשתנים החובה** מהתבנית ב-`/config.py` - אלו שספריית shared דורשת
2. **אי אפשר לדלג על משתנה** שספריית shared צריכה
3. **הוסף משתנים פנימיים** של השירות לפי הצורך (מפתחות API, הגדרות ספציפיות)
4. **וודא שכל המשתנים מתועדים** עם הסבר מה הם עושים
5. **צור מופע `config`** בסוף הקובץ

### 🟢 מדריך להוספת משתנים פנימיים

**משתנים מהתבנית הם בסיס חובה!** על הבסיס הזה, כל שירות יכול להוסיף את המשתנים הפנימיים שלו.

#### דוגמאות למשתנים פנימיים:

**שירות YouTube:**
```python
# משתנים פנימיים ספציפיים ל-YouTube
self.api_key = os.getenv("YOUTUBE_API_KEY")  # מפתח API
self.max_results = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))  # כמות תוצאות
self.timeout = int(os.getenv("YOUTUBE_TIMEOUT", "30"))  # Timeout
```

**שירות אודיו:**
```python
# משתנים פנימיים ספציפיים לעיבוד אודיו
self.threads = int(os.getenv("AUDIO_THREADS", "4"))  # כמות threads
self.temp_dir = os.getenv("AUDIO_TEMP_DIR", "/tmp")  # תיקיית זמני
```

#### עקרונות להוספת משתנים פנימיים:

1. **תמיד על בסיס חובה** - קודם להעתיק משתנים שספריית shared דורשת
2. **קידומת שירות** (YOUTUBE_, AUDIO_, וכו')
3. **ברירת מחדל הגיונית**
4. **תיעוד מה המשתנה עושה**

### 🎯 יתרונות הגישה הזו:
1. **ספריית shared עובדת** - כל הכלים מקבלים את המשתנים שהם צריכים
2. **עצמאות מלאה** - כל קונטיינר רואה רק מה שהוא צריך
3. **גמישות** - כל שירות יכול להוסיף משתנים פנימיים
4. **אבטחה** - אין חשיפה למשתנים של שירותים אחרים
5. **תחזוקה קלה** - שינוי בספריית shared דורש עדכון תבנית בלבד