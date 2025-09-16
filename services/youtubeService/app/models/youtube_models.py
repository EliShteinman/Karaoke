from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    video_id: str
    title: str
    channel: str
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    published_at: Optional[str] = None
    view_count: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]

class DownloadRequest(BaseModel):
    video_id: str
    title: str
    channel: str
    duration: int
    thumbnail: str

class DownloadResponse(BaseModel):
    status: str
    video_id: str
    message: str

# Kafka message models
class SongDownloadedMessage(BaseModel):
    video_id: str
    status: str
    metadata: Dict[str, Any]
    timestamp: str

class AudioProcessRequestMessage(BaseModel):
    video_id: str
    action: str

class TranscriptionRequestMessage(BaseModel):
    video_id: str
    action: str

# Error models
class DownloadErrorMessage(BaseModel):
    video_id: str
    status: str
    error: Dict[str, Any]
