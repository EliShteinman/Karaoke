# הגדרות קונפיגורציה - פרויקט קריוקי עברי

מדריך מלא לכל משתני הסביבה והגדרות הקונפיגורציה עבור כל השירותים.

## 📋 סקירה כללית

הפרויקט משתמש במשתני סביבה להגדרת כל השירותים. כל שירות יכול לעבוד עם ברירות מחדל או עם הגדרות מותאמות.

## ⚙️ משתני סביבה לפי שירות

### 📡 Kafka Configuration

```bash
# חיבור לשרת Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# שמות Topics עבור הפרויקט
KAFKA_TOPIC_DOWNLOAD_REQUESTED=song.download.requested
KAFKA_TOPIC_DOWNLOADED=song.downloaded
KAFKA_TOPIC_AUDIO_PROCESS=audio.process.requested
KAFKA_TOPIC_VOCALS_PROCESSED=audio.vocals_processed
KAFKA_TOPIC_TRANSCRIPTION=transcription.process.requested
KAFKA_TOPIC_TRANSCRIPTION_DONE=transcription.done

# קבוצות Consumer
KAFKA_CONSUMER_GROUP_YOUTUBE=youtube-service
KAFKA_CONSUMER_GROUP_AUDIO=audio-service
KAFKA_CONSUMER_GROUP_TRANSCRIPTION=transcription-service
```

### 🔍 Elasticsearch Configuration

```bash
# הגדרות חיבור
ELASTICSEARCH_SCHEME=http                    # או https
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic              # אופציונלי
ELASTICSEARCH_PASSWORD=password123          # אופציונלי

# שמות אינדקסים
ELASTICSEARCH_SONGS_INDEX=songs
ELASTICSEARCH_LOGS_INDEX=logs
```

### 💾 File Storage Configuration

```bash
# אחסון קבצים
STORAGE_BASE_PATH=/shared                   # נתיב בסיס לvolume
STORAGE_TYPE=volume                         # volume או s3

# הגדרות S3 (לעתיד)
STORAGE_S3_BUCKET=my-karaoke-bucket
STORAGE_S3_REGION=us-east-1
STORAGE_S3_ACCESS_KEY=YOUR_ACCESS_KEY
STORAGE_S3_SECRET_KEY=YOUR_SECRET_KEY
```

### 📝 Logger Configuration

```bash
# הגדרות לוגינג
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# שליחה לElasticsearch
LOG_ELASTICSEARCH_ENABLED=true
LOG_ELASTICSEARCH_SCHEME=http
LOG_ELASTICSEARCH_HOST=localhost
LOG_ELASTICSEARCH_PORT=9200
LOG_ELASTICSEARCH_INDEX=logs
```

### 🎵 YouTube Service Configuration

```bash
# YouTube API
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
YOUTUBE_MAX_RESULTS=10

# הגדרות הורדה
YOUTUBE_DOWNLOAD_QUALITY=bestaudio
YOUTUBE_DOWNLOAD_FORMAT=mp3
```

### 🎤 Audio Service Configuration

```bash
# עיבוד שמע
AUDIO_VOCAL_REMOVAL_METHOD=spleeter         # spleeter, uvr, etc.
AUDIO_OUTPUT_FORMAT=mp3
AUDIO_SAMPLE_RATE=44100
AUDIO_BITRATE=128k
```

### 🗣️ Transcription Service Configuration

```bash
# זיהוי דיבור
TRANSCRIPTION_MODEL_NAME=whisper-base       # whisper-tiny, whisper-base, etc.
TRANSCRIPTION_LANGUAGE=auto                 # he, en, auto
TRANSCRIPTION_OUTPUT_FORMAT=lrc             # lrc, srt, txt
```

### 🌐 API Server Configuration

```bash
# שרת API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# CORS
API_CORS_ORIGINS=*                          # * או רשימה מופרדת פסיקים
```

### 🖥️ Streamlit Client Configuration

```bash
# אפליקציית Streamlit
STREAMLIT_TITLE=HebKaraoke
STREAMLIT_THEME=dark                        # dark או light

# חיבור ל-API
STREAMLIT_API_BASE_URL=http://localhost:8000
```

### 🏗️ Project Global Configuration

```bash
# מטא-דאטה של הפרויקט
PROJECT_NAME=HebKaraoke
PROJECT_VERSION=1.0.0
ENVIRONMENT=development                     # development, staging, production
```

## 🚀 דוגמאות שימוש

### שימוש בקוד Python

```python
from shared.config import config

# גישה לקונפיג ספציפי
kafka_servers = config.kafka.bootstrap_servers
es_host = config.elasticsearch.host
storage_path = config.storage.base_path

# בדיקת סביבה
if config.is_production():
    # הגדרות production
    pass
elif config.is_development():
    # הגדרות development
    pass
```

### קובץ .env לפיתוח

```bash
# .env - דוגמה לפיתוח מקומי
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Storage
STORAGE_BASE_PATH=/tmp/karaoke

# Logging
LOG_LEVEL=DEBUG

# Services
YOUTUBE_API_KEY=your-api-key-here
API_PORT=8000
STREAMLIT_API_BASE_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
```

### קובץ .env לייצור

```bash
# .env.production - דוגמה לייצור
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka-cluster:9092

# Elasticsearch
ELASTICSEARCH_SCHEME=https
ELASTICSEARCH_HOST=elasticsearch-cluster
ELASTICSEARCH_PORT=443
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=secure_password_123

# Storage
STORAGE_TYPE=s3
STORAGE_S3_BUCKET=production-karaoke-files
STORAGE_S3_REGION=us-east-1

# Logging
LOG_LEVEL=INFO
LOG_ELASTICSEARCH_ENABLED=true

# Services
API_HOST=0.0.0.0
API_PORT=80
API_DEBUG=false

# Environment
ENVIRONMENT=production
```

## 🐳 Docker Compose Example

```yaml
version: '3.8'

services:
  youtube-service:
    image: hebkaraoke/youtube-service
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - ELASTICSEARCH_HOST=elasticsearch
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - STORAGE_BASE_PATH=/data
      - LOG_LEVEL=INFO
    volumes:
      - karaoke-data:/data

  audio-service:
    image: hebkaraoke/audio-service
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - ELASTICSEARCH_HOST=elasticsearch
      - AUDIO_VOCAL_REMOVAL_METHOD=spleeter
      - STORAGE_BASE_PATH=/data
    volumes:
      - karaoke-data:/data

  api-server:
    image: hebkaraoke/api-server
    environment:
      - ELASTICSEARCH_HOST=elasticsearch
      - STORAGE_BASE_PATH=/data
      - API_PORT=8000
    ports:
      - "8000:8000"
    volumes:
      - karaoke-data:/data

volumes:
  karaoke-data:
```

## 🔧 Kubernetes ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hebkaraoke-config
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka-cluster:9092"
  ELASTICSEARCH_HOST: "elasticsearch-cluster"
  ELASTICSEARCH_PORT: "9200"
  STORAGE_TYPE: "s3"
  STORAGE_S3_BUCKET: "production-karaoke"
  STORAGE_S3_REGION: "us-east-1"
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
```

## ✅ בדיקת קונפיגורציה

### סקריפט בדיקה

```python
# check_config.py
from shared.config import config

def check_configuration():
    print("🔍 בדיקת קונפיגורציה")
    print(f"📡 Kafka: {config.kafka.bootstrap_servers}")
    print(f"🔍 Elasticsearch: {config.elasticsearch.url}")
    print(f"💾 Storage: {config.storage.base_path}")
    print(f"🌍 Environment: {config.environment}")

    # בדיקת חיבורים
    from shared.kafka import KafkaProducerAsync
    from shared.elasticsearch import elasticsearch_config

    print("\n🧪 בדיקת חיבורים:")
    try:
        producer = KafkaProducerAsync()
        print(f"✅ Kafka Producer: {producer.bootstrap_servers}")
    except Exception as e:
        print(f"❌ Kafka Error: {e}")

    try:
        es_info = elasticsearch_config.get_connection_info()
        print(f"✅ Elasticsearch: {es_info['url']}")
    except Exception as e:
        print(f"❌ Elasticsearch Error: {e}")

if __name__ == "__main__":
    check_configuration()
```

## 📚 הערות חשובות

### 🔒 אבטחה
- **לעולם לא** לכתוב סיסמאות בקוד
- השתמש בקבצי `.env` או secrets management
- בייצור השתמש ב-Kubernetes secrets או AWS Parameter Store

### 🏷️ שמות משתנים
- כל משתני הסביבה מתחילים בשם השירות: `KAFKA_`, `ELASTICSEARCH_`, וכו'
- השתמש באותם שמות בכל הסביבות
- השם חייב להיות באנגלית ובאותיות גדולות

### 🔄 ברירות מחדל
- כל משתנה יש לו ברירת מחדל סבירה לפיתוח מקומי
- בייצור מומלץ להגדיר במפורש את כל הערכים
- ברירות המחדל מתאימות ל-localhost development

### 🧪 בדיקות
- השתמש בסקריפט `check_config.py` לוודא שהכל תקין
- בדוק את כל החיבורים לפני הרצת השירותים
- כל שירות יכתוב לוג עם הקונפיגורציה בהפעלה