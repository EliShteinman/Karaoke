# 🎤 הנחיות Claude Code - HebKaraoke Microservices

## 🎯 המטרה שלך
צור מבנה מיקרו-שירותים מלא עם שלדים וחתימות פונקציות. **אל תכתוב לוגיקה עסקית** - השאר זאת למפתחים!

---

## 📁 צור מבנה פרויקט זה

```
HebKaraoke/
├── services/
│   ├── downloader/          # שירות הורדה מיוטיוב (מפתח A)
│   ├── processor/           # עיבוד אודיו (מפתח B)
│   ├── transcriber/         # תמלול עברי (מפתח C)
│   ├── lrc-generator/       # יצירת קריוקי (מפתח D)
│   └── ui/                  # ממשק Streamlit (מפתח E)
├── shared/                  # קוד משותף (צור את זה מלא!)
│   ├── utils/
│   ├── models/
│   ├── kafka/
│   ├── elasticsearch/
│   ├── mongodb/
│   └── logging/
├── infrastructure/
│   ├── docker/
│   └── kubernetes/
├── docker-compose.yml
└── README.md
```

---

## 🛠️ שלב 1: צור Git Branches

צור 6 ברנצ'ים:
- `feature/downloader-service` (מפתח A)
- `feature/processor-service` (מפתח B) 
- `feature/transcriber-service` (מפתח C)
- `feature/lrc-generator-service` (מפתח D)
- `feature/ui-service` (מפתח E)
- `feature/shared-infrastructure` (מנהל פרויקט)

---

## 🏗️ שלב 2: בנה תיקיית shared מלאה

**צור את כל הקבצים האלה עם חתימות פונקציות מלאות:**

### shared/utils/logger.py
- `class ESLogHandler(logging.Handler)` - שליחת לוגים ל-Elasticsearch
- `setup_logger(service_name: str) -> logging.Logger` - הגדרת logger לשירות
- `log_kafka_message(logger, topic, message)` - לוג הודעות Kafka

### shared/kafka/producer.py
- `class HebKaraokeProducer` - Kafka producer משותף
- `send_message(topic, message)` - שליחת הודעה
- `send_job_request(from_service, to_service, job_id, song_id, payload)` - בקשת עבודה

### shared/kafka/consumer.py
- `class HebKaraokeConsumer` - Kafka consumer משותף
- `start_listening(message_handler)` - התחלת האזנה
- `stop_listening()` - הפסקת האזנה

### shared/mongodb/client.py
- `class HebKaraokeDB` - MongoDB client עם GridFS
- `save_file(file_data, filename, metadata)` - שמירת קובץ
- `get_file(file_id)` - קבלת קובץ
- `save_metadata(collection, data)` - שמירת מטא-דאטה
- `get_metadata(collection, query)` - קבלת מטא-דאטה

### shared/elasticsearch/client.py
- `class HebKaraokeSearch` - Elasticsearch client
- `index_song_metadata(song_id, metadata)` - אינדקס מטא-דאטה
- `search_songs(query, language)` - חיפוש שירים
- `get_song_status(song_id)` - סטטוס עיבוד
- `update_processing_status(song_id, service, status)` - עדכון סטטוס

### shared/models/song.py
- `@dataclass SongMetadata` - מטא-דאטה של שיר
- `@dataclass TranscriptSegment` - קטע תמלול
- `@dataclass JobRequest` - בקשת עבודה

**בכל קובץ shared - כתוב חתימות מלאות עם docstrings בעברית, אבל בגוף הפונקציות כתוב רק `# TODO: מפתח - כתוב את הלוגיקה כאן` ו-`pass`**

---

## 🎯 שלב 3: צור שלדי שירותים

לכל שירות, צור:

### מבנה תיקיות אחיד:
```
services/[service_name]/
├── src/
│   ├── app.py              # FastAPI app ראשי (או Streamlit לUI)
│   ├── config/
│   │   └── settings.py     # הגדרות
│   └── [service_name]/     # לוגיקה עסקית
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md              # README בעברית!
```

### שירות הורדה (downloader)
**ברנץ': feature/downloader-service**

**FastAPI app עם endpoints:**
- `POST /download` - הורדת שיר מיוטיוב
- `GET /status/{job_id}` - סטטוס הורדה
- `GET /health` - בריאות שירות

**אחריויות (כתוב ב-README):**
- האזנה ל-Kafka: `youtube_download_requests`
- הורדה מיוטיוב עם yt-dlp
- המרה לאודיו WAV 16kHz mono
- שמירה ב-MongoDB GridFS
- שליחה ל-`audio_processing_requests`

**טכנולוגיות ב-requirements.txt:**
- fastapi, uvicorn, yt-dlp, ffmpeg-python, kafka-python, pymongo, elasticsearch

### שירות עיבוד (processor)
**ברנץ': feature/processor-service**

**FastAPI app עם Kafka consumer:**
- האזנה ל-`audio_processing_requests`
- endpoint `GET /health`

**אחריויות:**
- הפרדת vocals מ-accompaniment (spleeter/demucs)
- זיהוי BPM ו-beat detection
- נורמליזציה
- שליחה ל-`transcription_requests`

**טכנולוגיות:**
- fastapi, librosa, numpy, scipy, kafka-python, pymongo

### שירות תמלול (transcriber)
**ברנץ': feature/transcriber-service**

**FastAPI app עם Kafka consumer:**
- האזנה ל-`transcription_requests`

**אחריויות:**
- תמלול עם Whisper/Vosk
- עיבוד טקסט עברי
- יצירת segments עם timestamps
- שליחה ל-`lrc_generation_requests`

**טכנולוגיות:**
- fastapi, whisper, vosk, hebrew-tokenizer, elasticsearch

### שירות LRC (lrc-generator)
**ברנץ': feature/lrc-generator-service**

**FastAPI app עם Kafka consumer:**
- האזנה ל-`lrc_generation_requests`

**אחריויות:**
- המרה לפורמט LRC
- סנכרון עם beat detection
- טיפול ב-RTL עברית
- שליחה ל-`ui_notifications`

### שירות UI (ui)
**ברנץ': feature/ui-service**

**Streamlit app (לא FastAPI!):**
- עמודים: בית, העלאה, קריוקי, סטטוס
- תמיכה ב-RTL עברית
- CSS מותאם

**אחריויות:**
- העלאת קישורי יוטיוב
- נגן קריוקי עם סנכרון מילים
- מעקב סטטוס עבודות

**טכנולוגיות:**
- streamlit, streamlit-advanced-audio, plotly, kafka-python

---

## 📄 שלב 4: צור קבצי תצורה

### docker-compose.yml
צור עם שירותים:
- kafka, zookeeper, elasticsearch, mongodb, redis
- כל 5 השירותים שלנו
- הגדרות environment נכונות

### כל שירות צריך Dockerfile
- בסיס: python:3.11-slim
- התקנת dependencies מ-requirements.txt
- הגדרת WORKDIR
- EXPOSE של הport המתאים
- CMD להרצת השירות

---

## 📝 שלב 5: כתוב README בעברית לכל ברנץ'

לכל ברנץ' צור README.md בעברית עם:

### עבור מפתח A (downloader):
```markdown
# שירות הורדה - מפתח A

## המשימה שלך
את/ה אחראי/ת על הורדת שירים מיוטיוב והמרה לאודיו.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/downloader/
2. הוסף לוגיקה להורדה עם yt-dlp
3. המר לאודיו WAV 16kHz mono עם ffmpeg
4. שמור ב-MongoDB עם הקוד המשותף
5. שלח הודעה ל-Kafka topic: audio_processing_requests

## קבצים שעליך לכתוב:
- src/downloader/youtube_client.py
- src/downloader/audio_converter.py  
- src/downloader/metadata_manager.py

## הרצה:
```bash
cd services/downloader
python src/app.py
```

## בדיקה:
POST http://localhost:8000/download
```

### עבור מפתח B (processor):
```markdown
# שירות עיבוד אודיו - מפתח B

## המשימה שלך
את/ה אחראי/ת על הפרדת vocals והכנת האודיו לתמלול.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/processor/
2. הפרד vocals מ-accompaniment עם spleeter או demucs
3. זהה BPM ו-beat timing עם librosa
4. נרמל את האודיו
5. שלח ל-transcription_requests

## קבצים שעליך לכתוב:
- src/processor/vocal_separator.py
- src/processor/audio_normalizer.py
- src/processor/beat_detector.py
```

### וכן הלאה לכל מפתח...

---

## ⚠️ חשוב - מה לא לכתוב

**אל תכתוב:**
- לוגיקה עסקית בפונקציות
- קוד ל-yt-dlp, spleeter, whisper וכו'
- לוגיקה של עיבוד אודיו או תמלול
- UI components מלאים

**כן כתוב:**
- מבנה תיקיות מלא
- חתימות פונקציות עם docstrings
- import statements נכונים
- requirements.txt מלאים
- Dockerfile עובדים
- docker-compose.yml פונקציונלי
- README מפורטים בעברית

---

## ✅ בסוף - וודא שיש:

- [x] 6 ברנצ'ים
- [x] תיקיית shared מלאה עם חתימות
- [x] 5 שירותים עם מבנה בסיסי
- [x] docker-compose.yml עובד
- [x] README בעברית לכל מפתח
- [x] requirements.txt מלאים
- [x] Dockerfile לכל שירות

**עכשיו התחל לעבוד!**