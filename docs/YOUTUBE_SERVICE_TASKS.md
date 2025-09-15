# YouTube Service - רשימת משימות

## 🎯 תפקיד הסרוויס
שירות אחיד לחיפוש והורדה מYouTube עם אינטגרציה מלאה לתהליך העבודה

---

## 📋 משימות פיתוח

### 1. הכנת סביבת הפיתוח
- [ ] יצירת תיקיית `services/youtube-service/`
- [ ] הכנת `Dockerfile` לסרוויס
- [ ] יצירת `requirements.txt` עם YouTube API, yt-dlp, Kafka dependencies
- [ ] הגדרת משתני סביבה (YouTube API key, Kafka configs)

### 2. הגדרות YouTube API
- [ ] יצירת `app/config/youtube_config.py`:
  - API key management
  - Rate limiting settings
  - Search parameters (max results, filters)
- [ ] רישום ב-Google Console ו-YouTube Data API v3
- [ ] בדיקת quota limits והגדרת monitoring

### 3. פונקציונליות חיפוש

#### Search Service - קלט ופלט
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

#### משימות יישום
- [ ] יצירת `app/services/youtube_search.py`
- [ ] מימוש פונקציית `search_videos(query: str) -> List[VideoResult]`:
  - קריאה ל-YouTube Data API v3
  - פרסור תוצאות ל-format אחיד
  - סינון וידאו בלבד (לא playlists/channels)
  - החזרת 10 תוצאות מעובדות
- [ ] הוספת retry logic עם exponential backoff
- [ ] טיפול ב-API quota exceeded errors

#### HTTP Interface לחיפוש
- [ ] יצירת `app/routes/search.py` (אם נדרש)
- [ ] או אלטרנטיבה: direct call from API Server

### 4. פונקציונליות הורדה

#### Download Service - קלט ופלט
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

#### משימות יישום
- [ ] יצירת `app/services/youtube_download.py`
- [ ] התקנת yt-dlp והגדרת configurations:
  ```python
  ydl_opts = {
      'format': 'bestaudio/best',
      'outtmpl': '/shared/audio/%(id)s/original.%(ext)s',
      'extractaudio': True,
      'audioformat': 'mp3',
      'audioquality': '0',  # best quality
  }
  ```
- [ ] מימוש פונקציית `download_audio(video_id: str) -> str`:
  - הורדת שמע בפורמט MP3
  - יצירת תיקיית `/shared/audio/{video_id}/`
  - שמירת `original.mp3`
  - החזרת נתיב הקובץ

#### Error Handling
- [ ] טיפול בשגיאות הורדה:
  - Video not available / private / region blocked
  - Copyright restrictions
  - Network timeouts
  - Disk space issues
- [ ] לוגים מפורטים לכל שגיאה

### 5. אינטגרציה עם Kafka

#### Consumer - קבלת בקשות הורדה
**טופיק:** `song.download.requested`

**פורמט הודעה:**
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

- [ ] יצירת `app/consumers/download_consumer.py`
- [ ] האזנה לטופיק `song.download.requested`
- [ ] עיבוד הודעות ובדיקת פורמט
- [ ] קריאה לפונקציית download_audio

#### Producer - שליחת הודעות
- [ ] יצירת `app/services/kafka_producer.py`
- [ ] מימוש שליחה של 3 הודעות לאחר הורדה מוצלחת:

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

### 6. עדכון Elasticsearch
**עדכון מסמך השיר לאחר הורדה מוצלחת:**
```python
doc_update = {
    "file_paths.original": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "updated_at": "2025-09-15T10:32:15Z",
    "metadata.file_size": 3456789,
    "metadata.duration": 213
}
```

- [ ] יצירת `app/services/elasticsearch_updater.py`
- [ ] עדכון מסמך השיר לאחר הורדה מוצלחת:
  - הוספת `file_paths.original`
  - עדכון `updated_at`
  - שמירת metadata (duration, file_size)

### 7. ממשק וחיבורים
- [ ] יצירת `app/main.py` עם entry point
- [ ] הפעלת Kafka consumers
- [ ] בדיקות חיבור לשירותים
- [ ] Health check endpoints

### 8. ניטור ולוגים
- [ ] לוגים מפורטים לכל שלב:
  - Search requests ו-responses
  - Download progress
  - Kafka messages sent/received
  - Errors עם context מלא
- [ ] Metrics collection (מספר הורדות, שגיאות, וכו')

### 9. בדיקות
- [ ] Unit tests ל-search functionality
- [ ] Integration tests עם YouTube API (mock)
- [ ] Unit tests ל-download logic עם yt-dlp mocks
- [ ] End-to-end tests עם Kafka
- [ ] בדיקת production readiness

### 10. אופטימיזציה וביצועים
- [ ] Concurrent downloads (אך לא יותר מ-2-3 במקביל)
- [ ] Queue management לבקשות הורדה
- [ ] Rate limiting כדי לא לחרוג מ-YouTube quotas
- [ ] Cleanup של קבצים זמניים במקרה של כשל

---

## 🔧 טכנולוגיות נדרשות
- **google-api-python-client** - YouTube Data API v3
- **yt-dlp** - הורדת וידאו/שמע מYouTube
- **kafka-python** או **aiokafka** - Kafka integration
- **elasticsearch-py** - עדכון metadata
- **requests** - HTTP calls
- **asyncio** - Async operations

---

## 📦 Dependencies מוערכות
```txt
google-api-python-client==2.110.0
google-auth-oauthlib==1.1.0
yt-dlp==2023.11.16
kafka-python==2.0.2
elasticsearch==8.11.0
requests==2.31.0
aiofiles==23.2.1
python-dotenv==1.0.0
```

---

## 🚀 הערות חשובות

### YouTube API Quotas
- חיפוש: 100 units per request
- Daily quota: 10,000 units (100 חיפושים ביום)
- נדרש תכנון קפדני של השימוש

### yt-dlp Configuration
- תמיד להוריד באיכות הטובה ביותר
- המרה אוטומטית ל-MP3
- יצירת תיקיות לפי video_id

### Shared Storage Structure
```
/shared/audio/
├── {video_id}/
│   └── original.mp3
```

### זרימת עבודה אוטומטית
הסרוויס מפעיל **אוטומטית** את השלבים הבאים לאחר הורדה:
1. שולח אירוע "downloaded"
2. מפעיל עיבוד אודיו
3. מפעיל תמלול
4. **לא מחכה** לסיום - זה async!

### Error Recovery
במקרה של כשל בהורדה:
- עדכון Elasticsearch עם שגיאה
- שליחת Kafka message עם error status
- לא לשלוח את 2 הפקודות הבאות