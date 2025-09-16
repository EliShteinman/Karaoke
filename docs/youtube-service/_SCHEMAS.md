# YouTube Service - סכמות קלט ופלט

## סקירה כללית
YouTube Service מטפל בכל הלוגיקה הקשורה ל-YouTube: חיפוש שירים והורדת קבצי אודיו. השירות מקבל בקשות HTTP לחיפוש והורדה מ-API Server, יוצר את המסמך הראשוני ב-Elasticsearch, מוריד קבצים מ-YouTube, ומתזמן את תהליך העיבוד באמצעות Kafka (ללא נתיבי קבצים).

## קלט (Inputs)

### בקשות HTTP

#### חיפוש שירים
**Endpoint:** `/search` (פנימי מ-API Server)
**Method:** `POST`
**Content-Type:** `application/json`

**מבנה גוף הבקשה:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

### בקשת הורדה
**Endpoint:** `/download` (פנימי מ-API Server)
**Method:** `POST`
**Content-Type:** `application/json`

**מבנה גוף הבקשה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

### קלט מ-YouTube API
**API Call:** `youtube.search().list()`
**Parameters:**
- `q`: שאילתת החיפוש
- `part`: "snippet"
- `type`: "video"
- `maxResults`: 10

## פלט (Outputs)

### תגובות HTTP

#### תוצאות חיפוש
**Status Code:** `200 OK`
**Content-Type:** `application/json`

**מבנה התגובה:**
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

#### אישור בקשת הורדה
**Status Code:** `202 Accepted`
**Content-Type:** `application/json`

**מבנה התגובה:**
```json
{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Song queued for processing"
}
```

### קבצים למערכת הקבצים

#### קובץ האודיו המקורי
**נתיב קבוע:** `/shared/audio/{video_id}/original.mp3`
**פורמט:** MP3, 44.1kHz, stereo
**איכות:** 128kbps (או הטובה ביותר הזמינה)

**דוגמה:** `/shared/audio/dQw4w9WgXcQ/original.mp3`

### הודעות Kafka (3 הודעות נפרדות - רק video_id)

#### הודעה 1: אירוע סיום הורדה
**Topic:** `song.downloaded`

**מבנה ההודעה (ללא נתיבי קבצים):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "downloaded",
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

**מבנה ההודעה (רק video_id):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "remove_vocals"
}
```

#### הודעה 3: פקודת תמלול
**Topic:** `transcription.process.requested`

**מבנה ההודעה (רק video_id):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "transcribe"
}
```

### יצירה ועדכונים ב-Elasticsearch

#### יצירת מסמך ראשוני (לפני הורדה)
**פעולה:** `PUT /songs/_doc/{video_id}`

**מבנה המסמך הראשוני:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "artist": "Rick Astley",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "status": "downloading",
  "file_paths": {},
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-09-15T10:30:00Z"
}
```

#### עדכון לאחר הורדה מוצלחת
**פעולה:** `POST /songs/{video_id}/_update`

**מבנה העדכון:**
```json
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

### קלט מ-YTDLP

#### הגדרות YTDLP
**Format:** `bestaudio[ext=mp3]/best[ext=mp4]/best`
**Output Template:** `/shared/audio/{video_id}/original.%(ext)s`
**Options:**
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
    }]
}
```

## שגיאות ואירועי כשל

### Kafka Error Messages

#### שגיאת הורדה
**Topic:** `song.download.failed`

**מבנה ההודעה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "failed",
  "error": {
    "code": "DOWNLOAD_FAILED",
    "message": "Video not available in your region",
    "details": "Sign in to confirm your age",
    "timestamp": "2025-09-15T10:32:00Z",
    "service": "youtube_service"
  }
}
```

#### שגיאת YouTube API
**התגובה:** HTTP 500 לקלינט (API Server)

**מבנה תגובת השגיאה:**
```json
{
  "error": {
    "code": "YOUTUBE_API_ERROR",
    "message": "Quota exceeded",
    "api_response": "quotaExceeded",
    "timestamp": "2025-09-15T10:30:00Z"
  }
}
```

### קודי שגיאה אפשריים
- `DOWNLOAD_FAILED`: כשל בהורדה מיוטיוב
- `VIDEO_NOT_AVAILABLE`: הוידאו לא זמין
- `YOUTUBE_API_ERROR`: שגיאה ב-YouTube API
- `QUOTA_EXCEEDED`: מיצוי מכסת API
- `INVALID_VIDEO_ID`: video_id לא תקין
- `NETWORK_ERROR`: שגיאת רשת
- `STORAGE_ERROR`: שגיאה בשמירת קובץ

### עדכון Elasticsearch עם שגיאה
**פעולה:** `POST /songs/{video_id}/_update`

**מבנה העדכון:**
```json
{
  "doc": {
    "status": "failed",
    "error": {
      "code": "DOWNLOAD_FAILED",
      "message": "Video not available in your region",
      "timestamp": "2025-09-15T10:32:00Z",
      "service": "youtube_service"
    },
    "updated_at": "2025-09-15T10:32:00Z"
  }
}
```