# API Server - סכמות קלט ופלט

## סקירה כללית
API Server משמש כשער כניסה (Gateway) בלבד. הוא מקבל בקשות HTTP מ-Streamlit Client, מנתב אותן ל-YouTube Service, וקורא מידע מ-Elasticsearch לצורכי הצגה בלבד. הוא אינו יוצר או מעדכן נתונים במערכת.

## קלט (Inputs)

### בקשות HTTP

#### `POST /search`
**Endpoint:** `/search`
**Method:** `POST`
**Content-Type:** `application/json`

**מבנה גוף הבקשה:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

**סכמת Pydantic:**
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
```

#### `POST /download`
**Endpoint:** `/download`
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

**סכמת Pydantic:**
```python
class DownloadRequest(BaseModel):
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$')
    title: str = Field(..., min_length=1, max_length=300)
    channel: str = Field(..., min_length=1, max_length=100)
    duration: int = Field(..., gt=0)
    thumbnail: HttpUrl
```

#### `GET /songs`
**Endpoint:** `/songs`
**Method:** `GET`
**Query Parameters:** אין

#### `GET /songs/{video_id}/status`
**Endpoint:** `/songs/{video_id}/status`
**Method:** `GET`
**Path Parameters:** `video_id` (string, 11 תווים)

#### `GET /songs/{video_id}/download`
**Endpoint:** `/songs/{video_id}/download`
**Method:** `GET`
**Path Parameters:** `video_id` (string, 11 תווים)

## פלט (Outputs)

### תגובות HTTP

#### `POST /search` - Response
**Status Code:** `200 OK`
**Content-Type:** `application/json`

**מבנה תגובה (ממוען מ-YouTube Service):**
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

**סכמת Pydantic:**
```python
class SearchResult(BaseModel):
    video_id: str
    title: str
    channel: str
    duration: int
    thumbnail: HttpUrl
    published_at: datetime

class SearchResponse(BaseModel):
    results: List[SearchResult]
```

#### `POST /download` - Response
**Status Code:** `202 Accepted`
**Content-Type:** `application/json`

**מבנה תגובה (ממוען מ-YouTube Service):**
```json
{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Song queued for processing"
}
```

**סכמת Pydantic:**
```python
class DownloadResponse(BaseModel):
    status: Literal["accepted"]
    video_id: str
    message: str
```

#### `GET /songs` - Response
**Status Code:** `200 OK`
**Content-Type:** `application/json`

**מבנה תגובה (מחושבת מ-Elasticsearch):**
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

**סכמת Pydantic:**
```python
class SongListItem(BaseModel):
    video_id: str
    title: str
    artist: str
    status: str
    created_at: datetime
    thumbnail: HttpUrl
    duration: int
    files_ready: bool

class SongsResponse(BaseModel):
    songs: List[SongListItem]
```

#### `GET /songs/{video_id}/status` - Response
**Status Code:** `200 OK`
**Content-Type:** `application/json`

**מבנה תגובה (מחושבת מ-Elasticsearch):**
```json
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

**סכמת Pydantic:**
```python
class Progress(BaseModel):
    download: bool
    audio_processing: bool
    transcription: bool
    files_ready: bool

class StatusResponse(BaseModel):
    video_id: str
    status: str
    progress: Progress
```

#### `GET /songs/{video_id}/download` - Response
**Status Code:** `200 OK`
**Content-Type:** `application/zip`

**פורמט:** קובץ ZIP המכיל:
- `vocals_removed.mp3` (קובץ שמע ללא ווקאל)
- `lyrics.lrc` (קובץ כתוביות עם timestamps)

### בקשות HTTP ל-YouTube Service (פנימיות)

#### חיפוש שירים
**Endpoint:** `POST /search` (YouTube Service)
**מבנה הבקשה הפנימית:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

#### בקשת הורדה
**Endpoint:** `POST /download` (YouTube Service)
**מבנה הבקשה הפנימית (העברה מלאה):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

## קריאות מ-Elasticsearch (קריאה בלבד)

### שאילתת שירים מוכנים
**פעולה:** `POST /songs/_search`

**שאילתה:**
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

### שליפת מסמך שיר ספציפי
**פעולה:** `GET /songs/_doc/{video_id}`

**תגובת Elasticsearch:**
```json
{
  "_source": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "artist": "Rick Astley",
    "status": "processing",
    "file_paths": {
      "original": "/shared/audio/dQw4w9WgXcQ/original.mp3",
      "vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
      "lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc"
    },
    "created_at": "2025-09-15T10:30:00Z",
    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "duration": 213
  }
}
```

## קריאות מ-Shared Storage (קריאה בלבד)

### קריאת קבצי קריוקי מוכנים
**נתיבים:**
- **אודיו ללא ווקאל:** `/shared/audio/{video_id}/vocals_removed.mp3`
- **כתוביות:** `/shared/audio/{video_id}/lyrics.lrc`

**מטרה:** יצירת קובץ ZIP להורדה ללקוח

## לוגיקת חישוב סטטוס פנימית

### קביעת התקדמות
```python
def calculate_progress(elasticsearch_doc) -> Progress:
    file_paths = elasticsearch_doc.get("file_paths", {})

    return Progress(
        download=bool(file_paths.get("original")),
        audio_processing=bool(file_paths.get("vocals_removed")),
        transcription=bool(file_paths.get("lyrics")),
        files_ready=bool(
            file_paths.get("vocals_removed") and
            file_paths.get("lyrics") and
            file_paths.get("vocals_removed") != "" and
            file_paths.get("lyrics") != ""
        )
    )
```

### קביעת שיר מוכן
```python
def is_song_ready(elasticsearch_doc) -> bool:
    file_paths = elasticsearch_doc.get("file_paths", {})
    return (
        file_paths.get("vocals_removed") and
        file_paths.get("lyrics") and
        file_paths.get("vocals_removed") != "" and
        file_paths.get("lyrics") != ""
    )
```

## קודי שגיאה

### `POST /search` - שגיאות
- **400 Bad Request:** שאילתה לא תקינה
- **503 Service Unavailable:** YouTube Service לא זמין
- **500 Internal Server Error:** שגיאה פנימית

### `POST /download` - שגיאות
- **400 Bad Request:** נתוני השיר לא תקינים
- **503 Service Unavailable:** YouTube Service לא זמין
- **500 Internal Server Error:** שגיאה פנימית

### `GET /songs/{video_id}/status` - שגיאות
- **404 Not Found:** השיר לא נמצא ב-Elasticsearch
- **503 Service Unavailable:** Elasticsearch לא זמין
- **500 Internal Server Error:** שגיאה פנימית

### `GET /songs/{video_id}/download` - שגיאות
- **404 Not Found:** השיר לא נמצא או לא מוכן
- **400 Bad Request:** קבצים חסרים או פגומים
- **503 Service Unavailable:** Elasticsearch או Storage לא זמינים
- **500 Internal Server Error:** שגיאה ביצירת ZIP

## הגדרות HTTP Client פנימי

### YouTube Service Client
```python
youtube_client_config = {
    "base_url": "http://youtube-service:8001",
    "timeout": 30.0,
    "retries": 3,
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "API-Server/1.0"
    }
}
```

### Elasticsearch Client (Read-Only)
```python
elasticsearch_config = {
    "hosts": ["http://elasticsearch:9200"],
    "timeout": 10.0,
    "max_retries": 3,
    "retry_on_timeout": True,
    "sniff_on_start": False,
    "sniff_on_connection_fail": False
}
```

**הערה חשובה:** כל הפעולות ב-Elasticsearch הן קריאה בלבד. אין יצירה, עדכון או מחיקה של מסמכים.

**הערה חשובה:** אין תקשורת עם Kafka. כל התיזמור מתבצע ב-YouTube Service בלבד.