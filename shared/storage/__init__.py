"""
Storage package for HebKaraoke project
Handles all file storage operations with support for different storage backends
"""

from .file_storage import (
    KaraokeFileManager,
    VolumeFileStorage,
    FileStorageInterface,
    create_file_manager
)

__all__ = [
    "KaraokeFileManager",
    "VolumeFileStorage",
    "FileStorageInterface",
    "create_file_manager"
]