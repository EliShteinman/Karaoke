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
    status: str = Field(..., description="Download status (accepted)")
    message: str = Field(..., description="Status message")
    video_id: str = Field(..., description="YouTube video ID")


class Progress(BaseModel):
    """Schema for processing progress from API Server"""
    download: bool = Field(default=False, description="Download stage completed")
    audio_processing: bool = Field(default=False, description="Audio processing stage completed")
    transcription: bool = Field(default=False, description="Transcription stage completed")
    files_ready: bool = Field(default=False, description="Files ready for download")


class SongStatus(BaseModel):
    """Schema for song processing status response"""
    video_id: str = Field(..., description="YouTube video ID")
    status: str = Field(..., description="Overall processing status")
    progress: Progress = Field(..., description="Processing progress details")


class SongListItem(BaseModel):
    """Schema for songs in the library"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Artist name")
    status: str = Field(..., description="Song processing status")
    created_at: str = Field(..., description="Creation datetime")
    thumbnail: str = Field(..., description="Thumbnail URL")
    duration: int = Field(..., description="Duration in seconds")
    progress: Progress = Field(..., description="Processing progress details")
    files_ready: bool = Field(..., description="Whether files are ready for download")


class SongsResponse(BaseModel):
    """Schema for songs response from API Server"""
    songs: List[SongListItem] = Field(default_factory=list, description="List of songs")


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
    library_songs: List[SongListItem] = Field(default_factory=list, description="Cached library songs")
    song_to_play: Optional[SongListItem] = Field(None, description="Currently selected song for playback")

    class Config:
        arbitrary_types_allowed = True