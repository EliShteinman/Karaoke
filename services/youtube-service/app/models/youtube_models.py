from pydantic import BaseModel
from typing import List, Optional

# --- קיימים ---
class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: Optional[str] = None
    published_at: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]

# --- חדש ---
class DownloadRequest(BaseModel):
    video_id: str

class DownloadResponse(BaseModel):
    video_id: str
    status: str
    file_path: Optional[str] = None
    error: Optional[str] = None
