# YouTube Service - סכמות קלט ופלט

## סקירה כללית
מסמך זה מכיל את הסכמות המלאות לשירות YouTube כפי שהוגדר באדריכלות הנכונה.

**עקרונות מרכזיים:**
- YouTube Service הוא שירות FastAPI עצמאי
- הוא יוצר ומעדכן מסמכים ב-Elasticsearch
- הוא שולח ל-Kafka רק IDs של שירים
- השירותים האחרים מקבלים מידע מ-Elasticsearch

---

## 1. FastAPI Routes

### `POST /search` - חיפוש שירים

**קלט מ-API Server:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

**Schema קלט (Pydantic):**
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)

class YouTubeSearchClient:
    def search_videos(self, query: str) -> List[dict]:
        """Search YouTube API for videos"""
        # Direct call to YouTube API
        youtube = build('youtube', 'v3', developerKey=API_KEY)

        request = youtube.search().list(
            part='snippet',
            q=query,
            maxResults=10,
            type='video',
            order='relevance'
        )

        response = request.execute()
        return response['items']
```

**פלט ל-API Server:**
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

---

## 2. `POST /download` - הורדת שיר

**קלט מ-API Server:**
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
    duration: int = Field(..., gt=0, lt=7200)
    thumbnail: str = Field(..., regex=r'^https?://.+')
```

**פלט ל-API Server:**
```json
{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Download started"
}
```

---

## 3. Pipeline פנימי - הורדה ועיבוד

### שלב 1: יצירת מסמך ב-Elasticsearch

**Schema מסמך התחלתי:**
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
  "updated_at": "2025-09-15T10:30:00Z",
  "file_paths": {},
  "search_text": "rick astley never gonna give you up rickroll"
}
```

### שלב 2: הורדה עם yt-dlp

**Schema הורדה:**
```python
class YTDLPDownloader:
    def download_audio(self, video_id: str, output_dir: str) -> dict:
        """Download audio using yt-dlp"""

        output_path = f"{output_dir}/{video_id}/original.mp3"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

                return {
                    "success": True,
                    "file_path": output_path,
                    "file_size": os.path.getsize(output_path)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
```

### שלב 3: עדכון Elasticsearch

**עדכון לאחר הורדה מוצלחת:**
```json
{
  "_id": "dQw4w9WgXcQ",
  "doc": {
    "status": "processing",
    "updated_at": "2025-09-15T10:32:00Z",
    "file_paths": {
      "original": "/shared/audio/dQw4w9WgXcQ/original.mp3"
    },
    "download_metadata": {
      "file_size": 4567890,
      "download_time": 45.2,
      "quality": "192kbps"
    }
  }
}
```

### שלב 4: שליחה ל-Kafka

**הודעות Kafka (רק IDs!):**

**הודעה 1 - סיום הורדה:**
```json
{
  "topic": "song.downloaded",
  "message": {
    "video_id": "dQw4w9WgXcQ",
    "status": "downloaded",
    "timestamp": "2025-09-15T10:32:00Z"
  }
}
```

**הודעה 2 - בקשת עיבוד אודיו:**
```json
{
  "topic": "audio.process.requested",
  "message": {
    "video_id": "dQw4w9WgXcQ",
    "action": "remove_vocals",
    "timestamp": "2025-09-15T10:32:00Z"
  }
}
```

**הודעה 3 - בקשת תמלול:**
```json
{
  "topic": "transcription.process.requested",
  "message": {
    "video_id": "dQw4w9WgXcQ",
    "action": "transcribe",
    "timestamp": "2025-09-15T10:32:00Z"
  }
}
```

---

## 4. Pipeline המלא - זרימת עבודה

### Schema Pipeline Manager:
```python
class DownloadPipeline:
    def __init__(self, elasticsearch_client, kafka_producer):
        self.es_client = elasticsearch_client
        self.kafka_producer = kafka_producer
        self.downloader = YTDLPDownloader()

    async def process_download(self, download_request: DownloadRequest) -> dict:
        """Process full download pipeline"""

        # 1. Create initial document
        await self.create_initial_document(download_request)

        # 2. Download audio
        download_result = self.downloader.download_audio(
            download_request.video_id,
            "/shared/audio"
        )

        if not download_result["success"]:
            await self.handle_download_error(download_request.video_id, download_result["error"])
            return {"status": "failed", "error": download_result["error"]}

        # 3. Update Elasticsearch with file path
        await self.update_after_download(download_request.video_id, download_result)

        # 4. Send Kafka messages (IDs only!)
        await self.send_processing_requests(download_request.video_id)

        return {"status": "accepted", "video_id": download_request.video_id}

    async def create_initial_document(self, request: DownloadRequest):
        """Create initial Elasticsearch document"""
        doc = {
            "title": request.title,
            "artist": self.extract_artist(request.title),
            "channel": request.channel,
            "duration": request.duration,
            "thumbnail": request.thumbnail,
            "status": "downloading",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "file_paths": {},
            "search_text": self.create_search_text(request)
        }

        await self.es_client.index(
            index="songs",
            id=request.video_id,
            body=doc
        )

    async def update_after_download(self, video_id: str, download_result: dict):
        """Update document after successful download"""
        update_doc = {
            "status": "processing",
            "updated_at": datetime.utcnow().isoformat(),
            "file_paths": {
                "original": download_result["file_path"]
            },
            "download_metadata": {
                "file_size": download_result["file_size"],
                "download_time": download_result.get("download_time", 0),
                "quality": "192kbps"
            }
        }

        await self.es_client.update(
            index="songs",
            id=video_id,
            body={"doc": update_doc}
        )

    async def send_processing_requests(self, video_id: str):
        """Send Kafka messages for processing (IDs only!)"""

        # Message 1: Download completed
        await self.kafka_producer.send("song.downloaded", {
            "video_id": video_id,
            "status": "downloaded",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Message 2: Request audio processing
        await self.kafka_producer.send("audio.process.requested", {
            "video_id": video_id,
            "action": "remove_vocals",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Message 3: Request transcription
        await self.kafka_producer.send("transcription.process.requested", {
            "video_id": video_id,
            "action": "transcribe",
            "timestamp": datetime.utcnow().isoformat()
        })
```

---

## 5. טיפול בשגיאות

### Schema שגיאות:
```python
class DownloadError(BaseModel):
    video_id: str
    error_code: Literal[
        "VIDEO_NOT_AVAILABLE",
        "REGION_BLOCKED",
        "AGE_RESTRICTED",
        "COPYRIGHT_BLOCKED",
        "DOWNLOAD_FAILED",
        "STORAGE_ERROR"
    ]
    error_message: str
    timestamp: str

async def handle_download_error(self, video_id: str, error: str):
    """Handle download errors"""

    # Update Elasticsearch
    error_doc = {
        "status": "failed",
        "updated_at": datetime.utcnow().isoformat(),
        "error": {
            "code": self.classify_error(error),
            "message": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    await self.es_client.update(
        index="songs",
        id=video_id,
        body={"doc": error_doc}
    )

    # Send error to Kafka
    await self.kafka_producer.send("song.download.failed", {
        "video_id": video_id,
        "error_code": self.classify_error(error),
        "timestamp": datetime.utcnow().isoformat()
    })
```

---

## 6. FastAPI App Structure

### Schema מבנה האפליקציה:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI(title="YouTube Service", version="1.0.0")

# Dependency injection
async def get_pipeline() -> DownloadPipeline:
    # Initialize clients
    es_client = AsyncElasticsearch([ELASTICSEARCH_URL])
    kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVERS)

    return DownloadPipeline(es_client, kafka_producer)

@app.post("/search", response_model=SearchResponse)
async def search_videos(request: SearchRequest):
    """Search YouTube for videos"""

    try:
        client = YouTubeSearchClient()
        results = client.search_videos(request.query)

        formatted_results = [
            SearchResult(
                video_id=item['id']['videoId'],
                title=item['snippet']['title'],
                channel=item['snippet']['channelTitle'],
                duration=get_video_duration(item['id']['videoId']),  # Additional API call
                thumbnail=item['snippet']['thumbnails']['high']['url'],
                published_at=item['snippet']['publishedAt']
            )
            for item in results
        ]

        return SearchResponse(results=formatted_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest, pipeline: DownloadPipeline = Depends(get_pipeline)):
    """Download video and start processing pipeline"""

    try:
        # Check if already exists
        existing = await pipeline.es_client.get(index="songs", id=request.video_id, ignore=[404])
        if existing['found']:
            raise HTTPException(status_code=409, detail="Song already exists")

        # Start pipeline (async)
        result = await pipeline.process_download(request)

        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result["error"])

        return DownloadResponse(
            status="accepted",
            video_id=request.video_id,
            message="Download started"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "youtube-service",
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 7. סיכום - תזרים נכון

### הזרימה המתוקנת:
```
1. API Server → YouTube Service: POST /download (HTTP)
2. YouTube Service → Elasticsearch: CREATE document (status="downloading")
3. YouTube Service → yt-dlp: Download audio file
4. YouTube Service → Elasticsearch: UPDATE document (file_paths.original + status="processing")
5. YouTube Service → Kafka: Send 3 messages with video_id only
6. YouTube Service → API Server: HTTP 202 response
7. Audio/Transcription Services → Kafka: Receive video_id
8. Audio/Transcription Services → Elasticsearch: GET document info by video_id
9. Audio/Transcription Services → Process files → UPDATE Elasticsearch
```

**עקרונות נכונים:**
- ✅ YouTube Service = FastAPI independent service
- ✅ YouTube Service creates & updates Elasticsearch documents
- ✅ Kafka messages contain only video_id + action
- ✅ All file paths come from Elasticsearch, not Kafka
- ✅ YouTube Service manages the download pipeline