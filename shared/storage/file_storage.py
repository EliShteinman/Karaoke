import logging
import os
import shutil
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Union

from shared.utils.path_utils import PathManager, build_relative_path

logger = logging.getLogger(__name__)


class FileStorageInterface(ABC):
    """
    Abstract interface for file storage
    Allows switching between local volume storage and external storage (S3, etc.)
    """

    @abstractmethod
    def save_file(self, file_content: bytes, file_path: str) -> str:
        """Save file content and return the actual path"""
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> bytes:
        """Read file content as bytes"""
        pass

    @abstractmethod
    def read_text_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read text file content as string"""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete file and return success status"""
        pass

    @abstractmethod
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        pass

    @abstractmethod
    def list_files(self, directory_path: str, pattern: str = "*") -> List[str]:
        """List files in directory matching pattern"""
        pass

    @abstractmethod
    def create_directory(self, directory_path: str) -> str:
        """Create directory if not exists and return path"""
        pass

    @abstractmethod
    def copy_file(self, source_path: str, destination_path: str) -> str:
        """Copy file and return destination path"""
        pass


class VolumeFileStorage(FileStorageInterface):
    """
    Local volume-based file storage implementation
    For the current phase where all files are stored in shared volumes
    """

    def __init__(self, base_path: str = "shared"):
        """
        Initialize with base path for shared storage

        Args:
            base_path: Base directory for file storage (default: shared)
        """
        # For base_path, we always want an absolute path
        if Path(base_path).is_absolute():
            self.base_path = Path(base_path).resolve()
        else:
            self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"VolumeFileStorage initialized with base path: {self.base_path}")

    def _get_full_path(self, file_path: str) -> Path:
        """Convert relative path to full path using cross-platform path handling"""
        path_obj = PathManager.normalize_path(file_path)
        if path_obj.is_absolute():
            return path_obj
        return self.base_path / path_obj

    def save_file(self, file_content: bytes, file_path: str) -> str:
        """Save file content and return the actual path"""
        full_path = self._get_full_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, "wb") as f:
                f.write(file_content)
            logger.info(f"File saved: {full_path}")
            return str(full_path)
        except Exception as e:
            logger.error(f"Failed to save file {full_path}: {e}")
            raise

    def read_file(self, file_path: str) -> bytes:
        """Read file content as bytes"""
        full_path = self._get_full_path(file_path)
        try:
            with open(full_path, "rb") as f:
                content = f.read()
            logger.debug(f"File read: {full_path} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {full_path}: {e}")
            raise

    def read_text_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read text file content as string"""
        full_path = self._get_full_path(file_path)
        try:
            with open(full_path, "r", encoding=encoding) as f:
                content = f.read()
            logger.debug(f"Text file read: {full_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Failed to read text file {full_path}: {e}")
            raise

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = self._get_full_path(file_path)
        exists = full_path.exists() and full_path.is_file()
        logger.debug(f"File exists check: {full_path} = {exists}")
        return exists

    def delete_file(self, file_path: str) -> bool:
        """Delete file and return success status"""
        full_path = self._get_full_path(file_path)
        try:
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted: {full_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {full_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {full_path}: {e}")
            return False

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        full_path = self._get_full_path(file_path)
        try:
            size = full_path.stat().st_size
            logger.debug(f"File size: {full_path} = {size} bytes")
            return size
        except Exception as e:
            logger.error(f"Failed to get file size {full_path}: {e}")
            raise

    def list_files(self, directory_path: str, pattern: str = "*") -> List[str]:
        """List files in directory matching pattern"""
        full_path = self._get_full_path(directory_path)
        try:
            if not full_path.exists():
                logger.warning(f"Directory not found: {full_path}")
                return []

            files = [str(p) for p in full_path.glob(pattern) if p.is_file()]
            logger.debug(f"Listed {len(files)} files in {full_path}")
            return files
        except Exception as e:
            logger.error(f"Failed to list files in {full_path}: {e}")
            return []

    def create_directory(self, directory_path: str) -> str:
        """Create directory if not exists and return path"""
        full_path = self._get_full_path(directory_path)
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory created/verified: {full_path}")
            return str(full_path)
        except Exception as e:
            logger.error(f"Failed to create directory {full_path}: {e}")
            raise

    def copy_file(self, source_path: str, destination_path: str) -> str:
        """Copy file and return destination path"""
        source_full = self._get_full_path(source_path)
        dest_full = self._get_full_path(destination_path)

        try:
            dest_full.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_full, dest_full)
            logger.info(f"File copied: {source_full} -> {dest_full}")
            return str(dest_full)
        except Exception as e:
            logger.error(f"Failed to copy file {source_full} -> {dest_full}: {e}")
            raise


class KaraokeFileManager:
    """
    High-level file manager for the Karaoke project
    Handles all file operations for songs (audio, lyrics, etc.)

    This is the SINGLE SOURCE OF TRUTH for all file path operations.
    All services must use these methods for path construction and resolution.
    """

    def __init__(self, storage: FileStorageInterface):
        """
        Initialize with a storage implementation

        Args:
            storage: File storage implementation (VolumeFileStorage, S3Storage, etc.)
        """
        self.storage = storage
        logger.info(f"KaraokeFileManager initialized with {type(storage).__name__}")

    def get_relative_path_original(self, video_id: str) -> str:
        """Get standardized relative path for original audio file"""
        return build_relative_path("audio", video_id, "original.mp3")

    def get_relative_path_vocals_removed(self, video_id: str) -> str:
        """Get standardized relative path for vocals removed audio file"""
        return build_relative_path("audio", video_id, "vocals_removed.mp3")

    def get_relative_path_lyrics(self, video_id: str) -> str:
        """Get standardized relative path for lyrics file"""
        return build_relative_path("audio", video_id, "lyrics.lrc")

    def get_full_path(self, relative_path: str) -> str:
        """Convert relative path to full absolute path for current platform"""
        full_path = self.storage._get_full_path(relative_path)
        return str(full_path)

    def save_original_audio(self, video_id: str, audio_content: bytes) -> str:
        """Save original downloaded audio file"""
        file_path = self.get_relative_path_original(video_id)
        return self.storage.save_file(audio_content, file_path)

    def save_vocals_removed_audio(self, video_id: str, audio_content: bytes) -> str:
        """Save processed audio with vocals removed"""
        file_path = self.get_relative_path_vocals_removed(video_id)
        return self.storage.save_file(audio_content, file_path)

    def save_lyrics_file(self, video_id: str, lyrics_content: str) -> str:
        """Save LRC lyrics file"""
        file_path = self.get_relative_path_lyrics(video_id)
        lyrics_bytes = lyrics_content.encode("utf-8")
        return self.storage.save_file(lyrics_bytes, file_path)

    def get_original_audio(self, video_id: str) -> bytes:
        """Get original audio file content"""
        file_path = self.get_relative_path_original(video_id)
        return self.storage.read_file(file_path)

    def get_vocals_removed_audio(self, video_id: str) -> bytes:
        """Get processed audio file content"""
        file_path = self.get_relative_path_vocals_removed(video_id)
        return self.storage.read_file(file_path)

    def get_lyrics(self, video_id: str) -> str:
        """Get lyrics file content as string"""
        file_path = self.get_relative_path_lyrics(video_id)
        return self.storage.read_text_file(file_path)

    def get_song_files_info(self, video_id: str) -> Dict[str, Dict]:
        """Get information about all files for a song"""
        files = {
            "original": self.get_relative_path_original(video_id),
            "vocals_removed": self.get_relative_path_vocals_removed(video_id),
            "lyrics": self.get_relative_path_lyrics(video_id),
        }

        info = {}
        for file_type, file_path in files.items():
            if self.storage.file_exists(file_path):
                info[file_type] = {
                    "path": file_path,
                    "exists": True,
                    "size": self.storage.get_file_size(file_path),
                }
            else:
                info[file_type] = {
                    "path": file_path,
                    "exists": False,
                    "size": 0,
                }

        return info

    def is_song_ready_for_karaoke(self, video_id: str) -> bool:
        """Check if song has both required files for karaoke"""
        vocals_path = self.get_relative_path_vocals_removed(video_id)
        lyrics_path = self.get_relative_path_lyrics(video_id)

        return (
            self.storage.file_exists(vocals_path)
            and self.storage.file_exists(lyrics_path)
        )

    def create_karaoke_package(self, video_id: str) -> bytes:
        """Create a ZIP package with vocals_removed.mp3 and lyrics.lrc"""
        if not self.is_song_ready_for_karaoke(video_id):
            raise ValueError(f"Song {video_id} is not ready for karaoke")

        vocals_content = self.get_vocals_removed_audio(video_id)
        lyrics_content = self.get_lyrics(video_id)

        # Create ZIP in memory
        import io
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("vocals_removed.mp3", vocals_content)
            zip_file.writestr("lyrics.lrc", lyrics_content.encode("utf-8"))

        zip_content = zip_buffer.getvalue()
        logger.info(f"Created karaoke package for {video_id} ({len(zip_content)} bytes)")
        return zip_content

    def delete_song_files(self, video_id: str) -> Dict[str, bool]:
        """Delete all files for a song and return deletion status"""
        files = {
            "original": self.get_relative_path_original(video_id),
            "vocals_removed": self.get_relative_path_vocals_removed(video_id),
            "lyrics": self.get_relative_path_lyrics(video_id),
        }

        results = {}
        for file_type, file_path in files.items():
            results[file_type] = self.storage.delete_file(file_path)

        logger.info(f"Deleted files for song {video_id}: {results}")
        return results

    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            audio_files = self.storage.list_files("audio", "**/*.mp3")
            lyrics_files = self.storage.list_files("audio", "**/*.lrc")

            total_audio_size = sum(
                self.storage.get_file_size(f) for f in audio_files
                if self.storage.file_exists(f)
            )

            return {
                "total_audio_files": len(audio_files),
                "total_lyrics_files": len(lyrics_files),
                "total_audio_size_bytes": total_audio_size,
                "total_audio_size_mb": round(total_audio_size / (1024 * 1024), 2),
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "total_audio_files": 0,
                "total_lyrics_files": 0,
                "total_audio_size_bytes": 0,
                "total_audio_size_mb": 0,
                "error": str(e),
            }


# Factory function for easy initialization
def create_file_manager(storage_type: str = "volume", **kwargs) -> KaraokeFileManager:
    """
    Create a KaraokeFileManager with the specified storage type

    Args:
        storage_type: "volume" for local volume storage (default)
        **kwargs: Additional arguments for storage initialization

    Returns:
        KaraokeFileManager instance
    """
    if storage_type == "volume":
        base_path = kwargs.get("base_path", "shared")
        storage = VolumeFileStorage(base_path)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")

    return KaraokeFileManager(storage)