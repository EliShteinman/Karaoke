# מפרט שרשרת קלט-פלט מלאה - מערכת קריוקי

## סקירה כוללת
מסמך זה מתאר את השרשרת המלאה של קלט ופלט במערכת הקריוקי, החל מבקשת המשתמש ב-Streamlit ועד לקבלת קובץ ZIP מוכן עם קבצי הקריוקי. כל שלב מתואר עם הנתונים המדויקים שעוברים בין השירותים.

---

## זרימה 1: חיפוש שירים

### 1.1 קלט מהמשתמש
**מקור:** Streamlit Client
**יעד:** API Server
**פרוטוקול:** HTTP POST

```json
POST /search
Content-Type: application/json

{
  "query": "rick astley never gonna give you up"
}
```

### 1.2 העברה ל-YouTube Service
**מקור:** API Server
**יעד:** YouTube Service
**פרוטוקול:** HTTP POST (פנימי)

```json
POST /internal/search
Content-Type: application/json

{
  "query": "rick astley never gonna give you up"
}
```

### 1.3 שאילתה ל-YouTube API
**מקור:** YouTube Service
**יעד:** YouTube Data API v3
**פרוטוקול:** HTTPS GET

```
GET https://www.googleapis.com/youtube/v3/search
?part=snippet
&q=rick+astley+never+gonna+give+you+up
&type=video
&maxResults=10
&key={API_KEY}
```

### 1.4 תגובה מ-YouTube API
**מקור:** YouTube Data API v3
**יעד:** YouTube Service

```json
{
  "items": [
    {
      "id": {"videoId": "dQw4w9WgXcQ"},
      "snippet": {
        "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
        "channelTitle": "RickAstleyVEVO",
        "publishedAt": "2009-10-25T09:57:33Z",
        "thumbnails": {
          "maxresdefault": {
            "url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
          }
        }
      }
    }
  ]
}
```

### 1.5 תגובה מעובדת ל-API Server
**מקור:** YouTube Service
**יעד:** API Server

```json
{
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
      "channel": "RickAstleyVEVO",
      "duration": 213,
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "published_at": "2009-10-25T09:57:33Z",
      "view_count": 1500000000
    }
  ]
}
```

### 1.6 תגובה למשתמש
**מקור:** API Server
**יעד:** Streamlit Client

```json
HTTP 200 OK
Content-Type: application/json

{
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
      "channel": "RickAstleyVEVO",
      "duration": 213,
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "published_at": "2009-10-25T09:57:33Z"
    }
  ]
}
```

---

## זרימה 2: בקשת הורדה ועיבוד

### 2.1 בקשת הורדה מהמשתמש
**מקור:** Streamlit Client
**יעד:** API Server
**פרוטוקול:** HTTP POST

```json
POST /download
Content-Type: application/json

{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

### 2.2 יצירת מסמך ב-Elasticsearch
**מקור:** API Server
**יעד:** Elasticsearch
**פרוטוקול:** HTTP PUT

```json
PUT /songs/_doc/dQw4w9WgXcQ
Content-Type: application/json

{
  "_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "artist": "Rick Astley",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "status": "downloading",
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-09-15T10:30:00Z",
  "file_paths": {},
  "search_text": "rick astley never gonna give you up"
}
```

### 2.3 שליחה לטופיק Kafka
**מקור:** API Server
**יעד:** Kafka Topic `song.download.requested`

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "action": "download",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

### 2.4 תגובה למשתמש
**מקור:** API Server
**יעד:** Streamlit Client

```json
HTTP 202 Accepted
Content-Type: application/json

{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Song queued for processing"
}
```

---

## זרימה 3: הורדה מיוטיוב

### 3.1 קבלת הודעה מ-Kafka
**מקור:** Kafka Topic `song.download.requested`
**יעד:** YouTube Service

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "action": "download",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

### 3.2 הורדה עם YTDLP
**מקור:** YouTube Service
**יעד:** YouTube/Shared Storage
**תהליך:** הרצת YTDLP command

```bash
yt-dlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 128K \
  --output "/shared/audio/%(id)s/original.%(ext)s"
```

**תוצר:** קובץ `/shared/audio/dQw4w9WgXcQ/original.mp3`

### 3.3 עדכון Elasticsearch
**מקור:** YouTube Service
**יעד:** Elasticsearch

```json
POST /songs/_update/dQw4w9WgXcQ
Content-Type: application/json

{
  "doc": {
    "file_paths.original": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "status": "processing",
    "updated_at": "2025-09-15T10:32:15Z",
    "metadata": {
      "original_size": 3456789,
      "download_time": 45.2,
      "source_quality": "128kbps"
    }
  }
}
```

### 3.4 שליחת 3 הודעות Kafka
**מקור:** YouTube Service
**יעד:** Kafka

#### הודעה 1: אירוע סיום הורדה
**Topic:** `song.downloaded`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "downloaded",
  "file_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "metadata": {
    "duration": 213,
    "bitrate": 128,
    "sample_rate": 44100,
    "file_size": 3456789,
    "format": "mp3"
  },
  "timestamp": "2025-09-15T10:32:15Z"
}
```

#### הודעה 2: פקודת עיבוד אודיו
**Topic:** `audio.process.requested`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "remove_vocals",
  "timestamp": "2025-09-15T10:32:16Z"
}
```

#### הודעה 3: פקודת תמלול
**Topic:** `transcription.process.requested`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "transcribe",
  "timestamp": "2025-09-15T10:32:17Z"
}
```

---

## זרימה 4: עיבוד אודיו (הסרת ווקאל)

### 4.1 קבלת הודעה מ-Kafka
**מקור:** Kafka Topic `audio.process.requested`
**יעד:** Audio Processing Service

```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "remove_vocals",
  "timestamp": "2025-09-15T10:32:16Z"
}
```

### 4.2 קריאת קובץ מקורי
**מקור:** Audio Processing Service
**יעד:** Shared Storage
**פעולה:** קריאת `/shared/audio/dQw4w9WgXcQ/original.mp3`

### 4.3 עיבוד ושמירת קובץ מעובד
**תהליך:** Center Channel Extraction אלגוריתם
**תוצר:** `/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3`

### 4.4 עדכון Elasticsearch
**מקור:** Audio Processing Service
**יעד:** Elasticsearch

```json
POST /songs/_update/dQw4w9WgXcQ
Content-Type: application/json

{
  "doc": {
    "file_paths.vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
    "updated_at": "2025-09-15T10:33:45Z",
    "processing_metadata.audio": {
      "processing_time": 45.2,
      "quality_score": 0.85,
      "algorithm": "center_channel_extraction",
      "original_size": 3456789,
      "processed_size": 3123456
    }
  }
}
```

### 4.5 שליחת אירוע סיום
**מקור:** Audio Processing Service
**יעד:** Kafka Topic `audio.vocals_processed`

```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed",
  "vocals_removed_path": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
  "processing_time": 45.2,
  "quality_score": 0.85,
  "algorithm_used": "center_channel_extraction",
  "metadata": {
    "original_size": 3456789,
    "processed_size": 3123456,
    "compression_ratio": 0.904,
    "snr_improvement": 12.3
  },
  "timestamp": "2025-09-15T10:33:45Z"
}
```

---

## זרימה 5: תמלול וכתוביות

### 5.1 קבלת הודעה מ-Kafka
**מקור:** Kafka Topic `transcription.process.requested`
**יעד:** Transcription Service

```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "transcribe",
  "timestamp": "2025-09-15T10:32:17Z"
}
```

### 5.2 תמלול עם Whisper
**תהליך:** Speech-to-Text עם Whisper Large v3
**קלט:** `/shared/audio/dQw4w9WgXcQ/original.mp3`

### 5.3 יצירת קובץ LRC
**תוצר:** `/shared/audio/dQw4w9WgXcQ/lyrics.lrc`

```lrc
[ar:Rick Astley]
[ti:Never Gonna Give You Up]
[al:Whenever You Need Somebody]
[au:Rick Astley]
[length:03:33]
[by:transcription_service]
[offset:0]

[00:00.50]We're no strangers to love
[00:04.15]You know the rules and so do I
[00:08.20]A full commitment's what I'm thinking of
[00:12.50]You wouldn't get this from any other guy
[00:16.80]I just wanna tell you how I'm feeling
[00:20.90]Gotta make you understand
[00:25.50]Never gonna give you up
[00:27.85]Never gonna let you down
[00:30.20]Never gonna run around and desert you
```

### 5.4 עדכון Elasticsearch
**מקור:** Transcription Service
**יעד:** Elasticsearch

```json
POST /songs/_update/dQw4w9WgXcQ
Content-Type: application/json

{
  "doc": {
    "file_paths.lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
    "updated_at": "2025-09-15T10:34:12Z",
    "processing_metadata.transcription": {
      "processing_time": 32.1,
      "confidence_score": 0.92,
      "language_detected": "en",
      "word_count": 156,
      "line_count": 32,
      "model_used": "whisper-large-v3"
    }
  }
}
```

### 5.5 שליחת אירוע סיום
**מקור:** Transcription Service
**יעד:** Kafka Topic `transcription.done`

```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "transcription_done",
  "lyrics_path": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
  "language": "en",
  "confidence": 0.92,
  "word_count": 156,
  "line_count": 32,
  "processing_time": 32.1,
  "model_used": "whisper-large-v3",
  "metadata": {
    "silence_detection": true,
    "background_noise_level": 0.05,
    "vocal_clarity": 0.88,
    "timestamps_accuracy": 0.91
  },
  "timestamp": "2025-09-15T10:34:12Z"
}
```

---

## זרימה 6: בדיקת סטטוס (Polling)

### 6.1 בקשת סטטוס מהמשתמש
**מקור:** Streamlit Client (כל 5 שניות)
**יעד:** API Server
**פרוטוקול:** HTTP GET

```
GET /songs/dQw4w9WgXcQ/status
```

### 6.2 שאילתה ל-Elasticsearch
**מקור:** API Server
**יעד:** Elasticsearch

```json
GET /songs/_doc/dQw4w9WgXcQ
```

### 6.3 תגובת Elasticsearch
**מקור:** Elasticsearch
**יעד:** API Server

```json
{
  "_source": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "status": "processing",
    "file_paths": {
      "original": "/shared/audio/dQw4w9WgXcQ/original.mp3",
      "vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
      "lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc"
    },
    "processing_metadata": {
      "audio": {"quality_score": 0.85},
      "transcription": {"confidence_score": 0.92}
    }
  }
}
```

### 6.4 תגובה למשתמש
**מקור:** API Server
**יעד:** Streamlit Client

```json
HTTP 200 OK
Content-Type: application/json

{
  "video_id": "dQw4w9WgXcQ",
  "status": "processing",
  "progress": {
    "download": true,
    "audio_processing": true,
    "transcription": true,
    "files_ready": true
  }
}
```

---

## זרימה 7: הורדת קבצי קריוקי מוכנים

### 7.1 רשימת שירים מוכנים
**מקור:** Streamlit Client
**יעד:** API Server

```
GET /songs
```

### 7.2 שאילתה מתקדמת ל-Elasticsearch
**מקור:** API Server
**יעד:** Elasticsearch

```json
POST /songs/_search
Content-Type: application/json

{
  "query": {
    "bool": {
      "must": [
        {"exists": {"field": "file_paths.vocals_removed"}},
        {"exists": {"field": "file_paths.lyrics"}},
        {"bool": {"must_not": [
          {"term": {"file_paths.vocals_removed": ""}},
          {"term": {"file_paths.lyrics": ""}}
        ]}}
      ]
    }
  }
}
```

### 7.3 תגובה עם שירים מוכנים
**מקור:** API Server
**יעד:** Streamlit Client

```json
{
  "songs": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "artist": "Rick Astley",
      "status": "processing",
      "created_at": "2025-09-15T10:30:00Z",
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "duration": 213,
      "files_ready": true
    }
  ]
}
```

### 7.4 בקשת הורדת קבצים
**מקור:** Streamlit Client
**יעד:** API Server

```
GET /songs/dQw4w9WgXcQ/download
```

### 7.5 קריאת קבצים מ-Shared Storage
**מקור:** API Server
**יעד:** Shared Storage

- **קריאת:** `/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3`
- **קריאת:** `/shared/audio/dQw4w9WgXcQ/lyrics.lrc`

### 7.6 יצירת וחזרת קובץ ZIP
**מקור:** API Server
**יעד:** Streamlit Client
**פרוטוקול:** HTTP Response

```
HTTP 200 OK
Content-Type: application/zip
Content-Disposition: attachment; filename="dQw4w9WgXcQ-karaoke.zip"

[Binary ZIP Data containing:]
├── vocals_removed.mp3    # Audio without vocals
└── lyrics.lrc           # Synchronized lyrics
```

---

## זרימה 8: נגינה בלקוח

### 8.1 חילוץ קבצי ZIP
**מקום:** Streamlit Client (מקומי)
**תהליך:**
- חילוץ `vocals_removed.mp3`
- חילוץ `lyrics.lrc`

### 8.2 פרסור קובץ LRC
**תהליך:** המרה למבנה נתונים פנימי

```python
lyrics_data = [
    {
        "timestamp": 0.5,
        "text": "We're no strangers to love",
        "duration": 3.65
    },
    {
        "timestamp": 4.15,
        "text": "You know the rules and so do I",
        "duration": 4.05
    }
]
```

### 8.3 נגינה וסנכרון
**תהליך מתמשך:**
- הפעלת קובץ האודיו
- מעקב אחר זמן נוכחי (כל 100ms)
- סנכרון הצגת כתוביות
- הדגשת שורה פעילה
- גלילה אוטומטית

---

## סיכום זרימת הנתונים המלאה

```
1. User Search Query → Streamlit → API Server → YouTube Service → YouTube API
                                                            ← YouTube Service ← API Server ← Streamlit ← User

2. User Download Request → Streamlit → API Server → Elasticsearch (create)
                                                  → Kafka (download.requested)
                                                  → YouTube Service → YTDLP → Shared Storage
                                                                   → Elasticsearch (update)
                                                                   → Kafka (3 messages)

3. Parallel Processing:
   Audio Service ← Kafka ← YouTube Service
   Audio Service → Shared Storage + Elasticsearch → Kafka (vocals_processed)

   Transcription Service ← Kafka ← YouTube Service
   Transcription Service → Shared Storage + Elasticsearch → Kafka (transcription_done)

4. Status Polling: User → Streamlit → API Server → Elasticsearch → API Server → Streamlit → User

5. Download Ready Files: User → Streamlit → API Server → Elasticsearch (query ready)
                                                       → Shared Storage (read files)
                                                       → ZIP creation
                                                       → Streamlit ← User

6. Local Playback: Streamlit → ZIP extract → Audio Player + LRC Parser → Synchronized Karaoke
```

זרימה זו מבטיחה עקביות, אמינות ואסינכרוניות מלאה בין כל רכיבי המערכת, כאשר כל שירות אחראי על התחום הספציפי שלו בלבד.