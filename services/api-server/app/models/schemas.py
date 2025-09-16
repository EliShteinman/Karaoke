from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal
from datetime import datetime

# --- Input Schemas ---

class SearchRequest(BaseModel):
    """Schema for the search request body."""
    query: str = Field(..., min_length=1, max_length=200, description="The search query string.")

class DownloadRequest(BaseModel):
    """Schema for the download request body, forwarded from the client."""
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$', description="YouTube video ID.")
    title: str = Field(..., min_length=1, max_length=300, description="Video title.")
    channel: str = Field(..., min_length=1, max_length=100, description="YouTube channel name.")
    duration: int = Field(..., gt=0, description="Video duration in seconds.")
    thumbnail: HttpUrl

# --- Output Schemas ---

class SearchResult(BaseModel):
    """Schema for a single search result item."""
    video_id: str
    title: str
    channel: str
    duration: int
    thumbnail: HttpUrl
    published_at: datetime

class SearchResponse(BaseModel):
    """Schema for the search response, containing a list of results."""
    results: List[SearchResult]

class DownloadResponse(BaseModel):
    """Schema for the response to a download request."""
    status: Literal["accepted"]
    video_id: str
    message: str

class SongListItem(BaseModel):
    """Schema for a single song item in the list of all songs."""
    video_id: str
    title: str
    artist: str
    status: str
    created_at: datetime
    thumbnail: HttpUrl
    duration: int
    files_ready: bool

class SongsResponse(BaseModel):
    """Schema for the response containing the list of all songs."""
    songs: List[SongListItem]

class Progress(BaseModel):
    """Schema representing the processing progress of a song."""
    download: bool
    audio_processing: bool
    transcription: bool
    files_ready: bool

class StatusResponse(BaseModel):
    """Schema for the response when checking a song's status."""
    video_id: str
    status: str
    progress: Progress
