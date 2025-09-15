# API Server - סכמות קלט ופלט

## סקירה כללית
מסמך זה מכיל את הסכמות המלאות לכל נקודות הגישה של ה-API Server.

**עקרון חשוב בנוגע לנתיבי קבצים:**
- נתיבי הקבצים מאוחסנים ומתקבלים **אך ורק מ-Elasticsearch**
- **אין העברת נתיבי קבצים דרך Kafka** (למעט בהודעות פנימיות בין השירותים)
- Kafka משמש רק להודעות פקודה ואירועים, לא למידע על מיקום קבצים

---

## 1. חיפוש שירים

### `POST /search`

**קלט:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

**Schema קלט (Pydantic):**
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200, description="שאילתת חיפוש")
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

**Schema פלט (Pydantic):**
```python
class SearchResult(BaseModel):
    video_id: str
    title: str
    channel: str
    duration: int  # בשניות
    thumbnail: str
    published_at: str  # ISO 8601 format

class SearchResponse(BaseModel):
    results: List[SearchResult]
```

---

## 2. בקשת הורדת שיר

### `POST /download`

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

**Schema קלט (Pydantic):**
```python
class DownloadRequest(BaseModel):
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$')
    title: str = Field(..., min_length=1, max_length=500)
    channel: str = Field(..., min_length=1, max_length=200)
    duration: int = Field(..., gt=0, lt=7200)  # מקסימום 2 שעות
    thumbnail: str = Field(..., regex=r'^https?://.+')
```

**פלט:**
```json
{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Song queued for processing"
}
```

**Schema פלט (Pydantic):**
```python
class DownloadResponse(BaseModel):
    status: Literal["accepted"]
    video_id: str
    message: str
```

**פעולות פנימיות:**

**קריאה ל-YouTube Service (HTTP POST):**
```python
# קריאה ל-YouTube Service
youtube_response = requests.post(
    f"{YOUTUBE_SERVICE_URL}/download",
    json=song_data,
    timeout=30
)
```

**אין יצירת מסמכים או שליחה ל-Kafka מה-API Server!**
YouTube Service מטפל בכל זה.

---

## 3. רשימת שירים מוכנים

### `GET /songs`

**קלט:** None

**שאילתת Elasticsearch (לוגיקת זיהוי שירים מוכנים):**
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

**Schema פלט (Pydantic):**
```python
class SongItem(BaseModel):
    video_id: str
    title: str
    artist: str
    status: str  # "downloading" | "processing" | "failed"
    created_at: str  # ISO 8601 format
    thumbnail: str
    duration: int
    files_ready: bool = True  # תמיד true כי השאילתה מחזירה רק שירים מוכנים

class SongsListResponse(BaseModel):
    songs: List[SongItem]
```

---

## 4. סטטוס שיר ספציפי

### `GET /songs/{video_id}/status`

**קלט:** `video_id` ב-URL path

**פלט:**
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

**Schema פלט (Pydantic):**
```python
class ProgressStatus(BaseModel):
    download: bool
    audio_processing: bool
    transcription: bool
    files_ready: bool

class SongStatusResponse(BaseModel):
    video_id: str
    status: Literal["downloading", "processing", "failed"]
    progress: ProgressStatus
```

**לוגיקת חישוב ה-progress:**
```python
def calculate_progress(elasticsearch_doc):
    progress = {
        "download": bool(elasticsearch_doc.get("file_paths", {}).get("original")),
        "audio_processing": bool(elasticsearch_doc.get("file_paths", {}).get("vocals_removed")),
        "transcription": bool(elasticsearch_doc.get("file_paths", {}).get("lyrics")),
    }
    progress["files_ready"] = progress["audio_processing"] and progress["transcription"]
    return progress
```

---

## 5. הורדת קבצי השיר המוכן

### `GET /songs/{video_id}/download`

**קלט:** `video_id` ב-URL path

**אימות תנאי מוקדם:**
```python
# בדיקה ש-Elasticsearch מחזיר שני נתיבים תקינים
def validate_song_ready(video_id):
    doc = elasticsearch.get(index="songs", id=video_id)
    vocals_path = doc.get("file_paths", {}).get("vocals_removed")
    lyrics_path = doc.get("file_paths", {}).get("lyrics")

    return (
        vocals_path and vocals_path.strip() != "" and
        lyrics_path and lyrics_path.strip() != "" and
        os.path.exists(vocals_path) and
        os.path.exists(lyrics_path)
    )
```

**פלט:**
- **Content-Type:** `application/zip`
- **ZIP Structure:**
  ```
  {video_id}_karaoke.zip
  ├── vocals_removed.mp3    # מוזיקה ללא ווקאל
  └── lyrics.lrc           # כתוביות עם timestamps
  ```

**Schema תגובה:**
```python
from fastapi.responses import StreamingResponse

# פלט כ-StreamingResponse עם ZIP
def create_zip_response(video_id: str, vocals_path: str, lyrics_path: str):
    return StreamingResponse(
        generate_zip_stream(vocals_path, lyrics_path),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={video_id}_karaoke.zip"}
    )
```

---

## 6. בדיקת תקינות (Health Check)

### `GET /health`

**קלט:** None

**פלט:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-15T10:30:00Z",
  "services": {
    "elasticsearch": "connected",
    "kafka": "connected"
  }
}
```

**Schema פלט (Pydantic):**
```python
class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    timestamp: str
    services: Dict[str, str]  # {"service_name": "connected|disconnected"}
```

---

## 7. טיפול בשגיאות

### Schema שגיאות אחיד:

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    video_id: Optional[str] = None
    timestamp: str

# דוגמאות שגיאות:
HTTP_404_NOT_FOUND = {
    "error": "SONG_NOT_FOUND",
    "message": "Song with specified video_id was not found",
    "video_id": "dQw4w9WgXcQ",
    "timestamp": "2025-09-15T10:30:00Z"
}

HTTP_409_CONFLICT = {
    "error": "SONG_ALREADY_EXISTS",
    "message": "Song is already being processed or completed",
    "video_id": "dQw4w9WgXcQ",
    "timestamp": "2025-09-15T10:30:00Z"
}

HTTP_425_TOO_EARLY = {
    "error": "SONG_NOT_READY",
    "message": "Song processing is not yet complete",
    "video_id": "dQw4w9WgXcQ",
    "timestamp": "2025-09-15T10:30:00Z"
}
```

---

## 8. עדכון דוקומנטציה - תיקונים נדרשים

### תיקון 1: הבהרת זרימת נתיבי קבצים

**בעיה שזוהתה:**
התיעוד המקורי לא הבהיר מספיק שנתיבי הקבצים נשלפים **אך ורק** מ-Elasticsearch ולא מועברים דרך Kafka.

**תיקון הנדרש:**
בקובץ `API_SERVER_TASKS.md` יש להוסיף הבהרה:

> **עיקרון חשוב:** ה-API Server לא מקבל נתיבי קבצים דרך Kafka. כל המידע על מיקום הקבצים נשלף מ-Elasticsearch בלבד. Kafka משמש אך ורק לפקודות ואירועים.

### תיקון 2: חיזוק ההגדרה של "שיר מוכן"

השאילתה ל-Elasticsearch צריכה להיות מתועדת בבירור כ**דרך היחידה** לזהות שירים מוכנים:

```python
# לוגיקת "שיר מוכן" - הגדרה מחייבת
def is_song_ready(video_id):
    doc = elasticsearch.get(index="songs", id=video_id)
    file_paths = doc.get("file_paths", {})

    return (
        file_paths.get("vocals_removed") and
        file_paths.get("lyrics") and
        file_paths["vocals_removed"].strip() != "" and
        file_paths["lyrics"].strip() != ""
    )
```

---

## 9. סיכום טכני

**תזרים המידע המתוקן (לפי האדריכלות הנכונה):**
1. **Streamlit → API Server** (בקשות HTTP)
2. **API Server → YouTube Service** (HTTP requests)
3. **YouTube Service → Elasticsearch** (יצירת/עדכון מסמכים)
4. **YouTube Service → Kafka** (הודעות עם IDs בלבד)
5. **Audio/Transcription Services → Elasticsearch** (קבלת מידע + עדכון תוצאות)
6. **API Server → Elasticsearch** (שאילתות לתצוגה)

**עקרונות מכוונים:**
- ✅ Elasticsearch = מקור האמת למטאדאטה ונתיבי קבצים
- ✅ Kafka = תקשורת אסינכרונית בין שירותים
- ❌ אין נתיבי קבצים ב-Kafka (פרט לצרכים פנימיים של שירותי העיבוד)
- ❌ אין גישה ישירה לקבצים מה-API Server