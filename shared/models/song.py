"""
מודלים משותפים לכל השירותים
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class SongMetadata:
    """
    מטא-דאטה של שיר
    """
    song_id: str
    title: str
    artist: str
    youtube_url: str
    duration: float
    language: str
    genre: Optional[str] = None
    bpm: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class TranscriptSegment:
    """
    קטע תמלול עם זמן
    """
    start_time: float
    end_time: float
    text: str
    confidence: float
    speaker_id: Optional[str] = None
    word_level_timestamps: Optional[List[Dict[str, Any]]] = None


@dataclass
class JobRequest:
    """
    בקשת עבודה בין שירותים
    """
    job_id: str
    song_id: str
    from_service: str
    to_service: str
    payload: Dict[str, Any]
    priority: int = 1
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ProcessingStatus:
    """
    סטטוס עיבוד שיר
    """
    song_id: str
    service: str
    status: str  # pending, processing, completed, failed
    progress: float = 0.0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None