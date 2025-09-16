"""
Data models and internal types for the API Server.
These complement the Pydantic schemas and provide additional internal data structures.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SongFileInfo:
    """Information about a song's files."""
    original_path: Optional[str] = None
    vocals_removed_path: Optional[str] = None
    lyrics_path: Optional[str] = None
    files_ready: bool = False


@dataclass
class ElasticsearchConfig:
    """Configuration for Elasticsearch connection."""
    scheme: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    songs_index: str = "songs"


@dataclass
class YouTubeServiceConfig:
    """Configuration for YouTube Service connection."""
    base_url: str
    timeout: float = 30.0
    retries: int = 3


@dataclass
class SongDocument:
    """Internal representation of a song document from Elasticsearch."""
    video_id: str
    title: str
    artist: str
    status: str
    created_at: datetime
    thumbnail: str
    duration: int
    file_paths: Dict[str, Any]
    metadata: Dict[str, Any]

    @classmethod
    def from_elasticsearch_doc(cls, doc: Dict[str, Any]) -> "SongDocument":
        """Create SongDocument from Elasticsearch document."""
        return cls(
            video_id=doc.get("video_id", ""),
            title=doc.get("title", ""),
            artist=doc.get("artist", ""),
            status=doc.get("status", ""),
            created_at=doc.get("created_at"),
            thumbnail=doc.get("thumbnail", ""),
            duration=doc.get("duration", 0),
            file_paths=doc.get("file_paths", {}),
            metadata=doc.get("metadata", {})
        )


@dataclass
class RepositoryConnectionInfo:
    """Information about repository connections for dependency injection."""
    elasticsearch_host: str
    elasticsearch_port: int
    elasticsearch_scheme: str
    elasticsearch_username: Optional[str] = None
    elasticsearch_password: Optional[str] = None
    songs_index: str = "songs"


@dataclass
class FileManagerConfig:
    """Configuration for file manager initialization."""
    storage_type: str = "volume"
    base_path: str = "/shared"