from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SearchRequest(BaseModel):
    """Schema for search requests to API Server"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query text")


class SearchResult(BaseModel):
    """Schema for individual search result from YouTube API"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Song title")
    channel: str = Field(..., description="YouTube channel name")
    duration: int = Field(..., description="Duration in seconds")
    thumbnail: str = Field(..., description="Thumbnail URL")
    published: Optional[str] = Field(None, description="Publication date")


class SearchResponse(BaseModel):
    """Schema for search response from API Server"""
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    total: Optional[int] = Field(None, description="Total number of results")


class DownloadRequest(BaseModel):
    """Schema for download requests to API Server"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Song title")
    channel: str = Field(..., description="YouTube channel name")
    duration: int = Field(..., description="Duration in seconds")
    thumbnail: str = Field(..., description="Thumbnail URL")


class DownloadResponse(BaseModel):
    """Schema for download response from API Server"""
    status: str = Field(..., description="Download status (queued, processing, completed, failed)")
    message: Optional[str] = Field(None, description="Status message")
    video_id: str = Field(..., description="YouTube video ID")


class SongStatusStage(BaseModel):
    """Schema for individual processing stage status"""
    download: str = Field(default="PENDING", description="Download stage status")
    audio_processing: str = Field(default="PENDING", description="Audio processing stage status")
    transcription: str = Field(default="PENDING", description="Transcription stage status")


class SongStatus(BaseModel):
    """Schema for song processing status response"""
    video_id: str = Field(..., description="YouTube video ID")
    overall_status: str = Field(..., description="Overall processing status")
    progress: int = Field(default=0, description="Progress percentage (0-100)")
    stages: SongStatusStage = Field(default_factory=SongStatusStage, description="Individual stage statuses")
    estimated_time: Optional[str] = Field(None, description="Estimated time remaining")


class LibrarySong(BaseModel):
    """Schema for songs in the library"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Song title")
    artist: str = Field(default="", description="Artist name")
    channel: str = Field(default="", description="YouTube channel name")
    duration: int = Field(default=0, description="Duration in seconds")
    thumbnail: str = Field(default="", description="Thumbnail URL")
    created_date: Optional[str] = Field(None, description="Creation date")
    file_paths: Dict[str, str] = Field(default_factory=dict, description="File paths for song assets")


class LibraryResponse(BaseModel):
    """Schema for library response from API Server"""
    songs: List[LibrarySong] = Field(default_factory=list, description="List of ready songs")
    total: int = Field(default=0, description="Total number of songs")


class LrcLine(BaseModel):
    """Schema for LRC lyric line"""
    timestamp: float = Field(..., description="Timestamp in seconds")
    text: str = Field(..., description="Lyric text")
    end_time: Optional[float] = Field(None, description="End timestamp in seconds")
    duration: Optional[float] = Field(None, description="Line duration in seconds")


class SessionState(BaseModel):
    """Schema for Streamlit session state management"""
    current_page: str = Field(default="search", description="Current active page")
    search_query: str = Field(default="", description="Last search query")
    search_results: List[SearchResult] = Field(default_factory=list, description="Current search results")
    download_requests: Dict[str, SearchResult] = Field(default_factory=dict, description="Active download tracking")
    library_songs: List[LibrarySong] = Field(default_factory=list, description="Cached library songs")
    song_to_play: Optional[LibrarySong] = Field(None, description="Currently selected song for playback")

    class Config:
        arbitrary_types_allowed = True