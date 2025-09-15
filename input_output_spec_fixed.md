# מפרט קלט ופלט - יישום קריוקי (גרסת MVP)

## 1. API Server

### HTTP Endpoints:

#### `POST /search`
**קלט:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

**פלט:**
```json
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

#### `POST /download`
**קלט:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

**פעולות פנימיות:**
1. **יצירת מסמך באלסטיק:**
```json
{
  "_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "artist": "Rick Astley",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "status": "downloading",
  "created_at": "2025-09-15T10:30:00Z",
  "file_paths": {},
  "search_text": "rick astley never gonna give you up"
}
```

2. **שליחה לקפקא:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "action": "download"
}
```

**פלט:**
```json
{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Song queued for processing"
}
```

#### `GET /songs`
**קלט:** None

**לוגיקת שאילתה מעודכנת (Elasticsearch):**
```json
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

**פלט:**
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

#### `GET /songs/{video_id}/status`
**קלט:** video_id בURL

**פלט:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "processing", // downloading | processing | failed (לא "ready" ב-MVP)
  "progress": {
    "download": true,
    "audio_processing": true,
    "transcription": true,
    "files_ready": true
  }
}
```

#### `GET /songs/{video_id}/download`
**קלט:** video_id בURL

**פלט:** ZIP עם הקבצים:
- `vocals_removed.mp3` (מוזיקה ללא ווקאל)
- `lyrics.lrc` (כתוביות עם timestamps)

---

## 2. YouTube Service

### פונקציה 1: חיפוש

**קלט (מ-API Server):**
```json
{
  "query": "rick astley never gonna"
}
```

**פלט (ל-API Server):**
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

### פונקציה 2: הורדה

**קלט (מ-API Server דרך Kafka):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "action": "download"
}
```

**פלט (קובץ):**
- מיקום: `/shared/audio/dQw4w9WgXcQ/original.mp3`
- פורמט: MP3, 44.1kHz, stereo

**פלט (ל-Kafka - 3 הודעות):**

**הודעה 1 - אירוע סיום הורדה:**
```json
{
  "topic": "song.downloaded",
  "message": {
    "video_id": "dQw4w9WgXcQ",
    "status": "downloaded",
    "file_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "metadata": {
      "duration": 213,
      "bitrate": 128,
      "sample_rate": 44100,
      "file_size": 3456789
    }
  }
}
```

**הודעה 2 - פקודת עיבוד אודיו:**
```json
{
  "topic": "audio.process.requested",
  "message": {
    "video_id": "dQw4w9WgXcQ",
    "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "action": "remove_vocals"
  }
}
```

**הודעה 3 - פקודת תמלול:**
```json
{
  "topic": "transcription.process.requested", 
  "message": {
    "video_id": "dQw4w9WgXcQ",
    "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "action": "transcribe"
  }
}
```

---

## 3. Audio Processing Service

**קלט (מ-Kafka):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "remove_vocals"
}
```

**קלט (קובץ):**
- מיקום: `/shared/audio/dQw4w9WgXcQ/original.mp3`

**פלט (קובץ):**
- מיקום: `/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3`
- פורמט: MP3, 44.1kHz, stereo (ללא ווקאל)

**פלט (עדכון Elasticsearch):**
```json
{
  "_id": "dQw4w9WgXcQ",
  "file_paths.vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
  "updated_at": "2025-09-15T10:33:45Z"
}
```

**פלט (ל-Kafka):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed",
  "vocals_removed_path": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
  "processing_time": 45.2,
  "quality_score": 0.85
}
```

---

## 4. Transcription Service

**קלט (מ-Kafka):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "transcribe"
}
```

**קלט (קובץ):**
- מיקום: `/shared/audio/dQw4w9WgXcQ/original.mp3`

**פלט (קובץ LRC):**
- מיקום: `/shared/audio/dQw4w9WgXcQ/lyrics.lrc`
- פורמט:
```lrc
[ar:Rick Astley]
[ti:Never Gonna Give You Up]
[00:00.50]We're no strangers to love
[00:04.15]You know the rules and so do I
[00:08.20]A full commitment's what I'm thinking of
[00:12.50]You wouldn't get this from any other guy
```

**פלט (עדכון Elasticsearch):**
```json
{
  "_id": "dQw4w9WgXcQ",
  "file_paths.lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
  "updated_at": "2025-09-15T10:34:12Z"
}
```

**פלט (ל-Kafka):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "transcription_done", 
  "lyrics_path": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
  "language": "en",
  "confidence": 0.92,
  "word_count": 156,
  "processing_time": 32.1
}
```

---

## 5. Streamlit Client - מפרט קלט/פלט

### חיפוש שירים:
**קלט מהמשתמש:** שאילתת חיפוש טקסט
**פלט למשתמש:** רשימת תוצאות עם thumbnails וכפתור "הורד"

### בחירת שיר להורדה:
**קלט מהמשתמש:** לחיצה על כפתור "הורד" 
**פלט למשתמש:** הודעת אישור וכפתור "עבור לנגן"

### מעקב אחר סטטוס:
**פעולה:** polling כל 5 שניות על API
**לוגיקה:** בדיקה של `progress.files_ready === true`
**פלט למשתמש:** progress bar עם שלבי העיבוד

### נגן קריוקי:

**קלט:**
- ZIP עם קבצים מ-`GET /songs/{video_id}/download`
- מטא-דאטה מ-`GET /songs/{video_id}/status`

**פעולות עיבוד:**
```python
# פרסור קובץ LRC
def parse_lrc(lrc_content):
    lines = []
    for line in lrc_content.split('\n'):
        if '[' in line and ']' in line:
            timestamp = extract_timestamp(line)  # [00:12.50] -> 12.5 seconds
            text = extract_text(line)            # "You wouldn't get this..."
            lines.append((timestamp, text))
    return lines

# סנכרון כתוביות
def sync_lyrics(current_time, lyrics_lines):
    active_line = find_current_line(current_time, lyrics_lines)
    next_line = find_next_line(current_time, lyrics_lines)
    return active_line, next_line
```

**פלט למשתמש:**
- נגן אודיו עם בקרות play/pause/seek
- הצגת כתוביות מסונכרנות
- הדגשת השורה הפעילה
- תצוגת מטא-דאטה (כותרת, אמן, תמונה)

---

## Kafka Topics Structure:

### Topic: `song.download.requested`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "action": "download",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

### Topic: `song.downloaded`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "downloaded",
  "file_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "timestamp": "2025-09-15T10:32:15Z"
}
```

### Topic: `audio.process.requested`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "remove_vocals"
}
```

### Topic: `transcription.process.requested`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3", 
  "action": "transcribe"
}
```

### Topic: `audio.vocals_processed`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed",
  "vocals_removed_path": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3"
}
```

### Topic: `transcription.done`
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "transcription_done",
  "lyrics_path": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc"
}
```

---

## Elasticsearch Document Structure:

### Index: `songs`

```json
{
  "_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "artist": "Rick Astley", 
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "status": "processing",
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-09-15T10:35:30Z",
  "file_paths": {
    "original": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
    "lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc"
  },
  "metadata": {
    "original_size": 3456789,
    "total_processing_time": 123.7,
    "quality_scores": {
      "audio_processing": 0.85,
      "transcription": 0.92
    }
  },
  "search_text": "rick astley never gonna give you up rickroll official video"
}
```

**הערה MVP:** השדה `status` ישאר על `processing` גם כאשר השיר מוכן. זיהוי שירים מוכנים נעשה על ידי בדיקת קיום שני השדות `vocals_removed` ו-`lyrics` ב-`file_paths`.

---

## Error Handling:

### שגיאות שכל שירות יכול להחזיר:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "failed",
  "error": {
    "code": "DOWNLOAD_FAILED", 
    "message": "Video not available in your region",
    "timestamp": "2025-09-15T10:32:00Z",
    "service": "youtube_service"
  }
}
```

### קודי שגיאה אפשריים:
- `DOWNLOAD_FAILED` - כשל בהורדה מיוטיוב
- `AUDIO_PROCESSING_FAILED` - כשל בהסרת ווקאל
- `TRANSCRIPTION_FAILED` - כשל בתמלול
- `FILE_NOT_FOUND` - קובץ לא נמצא
- `INVALID_FORMAT` - פורמט קובץ לא נתמך
- `ELASTICSEARCH_ERROR` - כשל בעדכון מטאדאטה

---

## דוגמאות זרימה מלאה (MVP):

### זרימה מוצלחת:
```
1. Streamlit → API: POST /download {"video_id": "dQw4w9WgXcQ"}
2. API → Elasticsearch: Create document with status="downloading"
3. API → Kafka: song.download.requested
4. YouTube Service → File System: Download original.mp3
5. YouTube Service → Kafka: song.downloaded (Event)
6. YouTube Service → Kafka: audio.process.requested (Command)
7. YouTube Service → Kafka: transcription.process.requested (Command)
8. Audio Service → File System: Create vocals_removed.mp3
9. Audio Service → Elasticsearch: Update file_paths.vocals_removed
10. Audio Service → Kafka: audio.vocals_processed
11. Transcription Service → File System: Create lyrics.lrc
12. Transcription Service → Elasticsearch: Update file_paths.lyrics
13. Transcription Service → Kafka: transcription.done
14. Streamlit polling → API: GET /songs → finds song via file_paths query
15. Streamlit → API: GET /songs/{video_id}/download → Download ZIP with both files
```

### זרימה עם שגיאה:
```
1-7. [כמו למעלה]
8. Audio Service → Kafka: {"status": "failed", "error": "AUDIO_PROCESSING_FAILED"}
9. Audio Service → Elasticsearch: Update status="failed"
10. Streamlit polling → API: GET /songs/{video_id}/status → {"status": "failed"}
```

### בדיקת קובץ מוכן ב-API Server:
```python
# פסאודו-קוד לבדיקת שיר מוכן
def is_song_ready(video_id):
    doc = elasticsearch.get(index="songs", id=video_id)
    return (
        doc["file_paths"].get("vocals_removed") and 
        doc["file_paths"].get("lyrics") and
        doc["file_paths"]["vocals_removed"] != "" and
        doc["file_paths"]["lyrics"] != ""
    )
```