"""
Data models and internal types for the API Server.
These complement the Pydantic schemas and provide additional internal data structures.
All models have complete type hints as required.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SongFileInfo:
    """Information about a song's files with complete type annotations."""
    original_path: Optional[str] = None
    vocals_removed_path: Optional[str] = None
    lyrics_path: Optional[str] = None
    files_ready: bool = False


@dataclass
class ElasticsearchConfig:
    """Configuration for Elasticsearch connection with complete type annotations."""
    scheme: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    songs_index: str = "songs"


@dataclass
class YouTubeServiceConfig:
    """Configuration for YouTube Service connection with complete type annotations."""
    base_url: str
    timeout: float = 30.0
    retries: int = 3


@dataclass
class SongDocument:
    """Internal representation of a song document from Elasticsearch with complete type annotations."""
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
        """Create SongDocument from Elasticsearch document with error handling."""
        try:
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
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Failed to create SongDocument from Elasticsearch doc: {e}")


@dataclass
class RepositoryConnectionInfo:
    """Information about repository connections for dependency injection with complete type annotations."""
    elasticsearch_host: str
    elasticsearch_port: int
    elasticsearch_scheme: str
    elasticsearch_username: Optional[str] = None
    elasticsearch_password: Optional[str] = None
    songs_index: str = "songs"


@dataclass
class FileManagerConfig:
    """Configuration for file manager initialization with complete type annotations."""
    storage_type: str = "volume"
    base_path: str = "shared"


@dataclass
class LoggerConfig:
    """Configuration for logger setup with complete type annotations."""
    name: str
    elasticsearch_url: str
    index: str
    level: str = "INFO"


@dataclass
class APIServerStatus:
    """Internal status representation for API server health checks."""
    status: str
    timestamp: datetime
    services_status: Dict[str, bool]
    error_message: Optional[str] = None