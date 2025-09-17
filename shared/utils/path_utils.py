"""
Cross-platform path utilities for the Karaoke project.

This module provides consistent path handling across Windows, macOS, and Linux.
All file operations should use these utilities to ensure cross-platform compatibility.
"""
import os
from pathlib import Path
from typing import Union, Optional


class PathManager:
    """
    Centralized path management for cross-platform compatibility.
    Uses pathlib.Path for consistent behavior across operating systems.
    """

    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """
        Normalize a path for the current platform.

        Args:
            path: Input path as string or Path object

        Returns:
            Normalized Path object (preserves relative/absolute nature)
        """
        if isinstance(path, str):
            # Convert backslashes to forward slashes for consistent processing
            path = path.replace('\\', '/')

        path_obj = Path(path)

        # Only resolve if it's already absolute, otherwise keep it relative
        if path_obj.is_absolute():
            return path_obj.resolve()
        else:
            # For relative paths, just normalize separators without resolving
            return path_obj

    @staticmethod
    def join(*parts: Union[str, Path]) -> Path:
        """
        Join path parts using the current platform's separator.

        Args:
            *parts: Path components to join

        Returns:
            Joined Path object
        """
        # Convert all parts to strings and normalize separators
        normalized_parts = []
        for part in parts:
            if isinstance(part, Path):
                normalized_parts.append(str(part))
            else:
                # Replace backslashes with forward slashes for consistent processing
                normalized_parts.append(str(part).replace('\\', '/'))

        return Path(*normalized_parts)

    @staticmethod
    def relative_to_base(path: Union[str, Path], base_path: Union[str, Path]) -> Path:
        """
        Get path relative to base path, handling different separator formats.

        Args:
            path: Full or relative path
            base_path: Base path to make relative to

        Returns:
            Relative Path object
        """
        # Normalize both paths first
        path_str = str(path).replace('\\', '/')
        base_str = str(base_path).replace('\\', '/')

        # Remove leading "./" from paths
        if path_str.startswith('./'):
            path_str = path_str[2:]
        if base_str.startswith('./'):
            base_str = base_str[2:]

        # If path starts with base_path, extract the relative part
        if path_str.startswith(base_str):
            # Remove the base path and any leading separator
            relative_part = path_str[len(base_str):].lstrip('/')
            return Path(relative_part) if relative_part else Path('.')

        # Special handling for cases like 'data/audio/video_id/file' with base 'data/audio'
        # The path should be relative to the storage base, so keep the full path
        if base_str.endswith('audio') and 'audio' in path_str:
            # Return the full path as relative - the file manager will handle the base
            return Path(path_str)

        # If base is contained within path, extract what comes after
        base_clean = base_str.rstrip('/')
        if base_clean in path_str:
            parts = path_str.split(base_clean, 1)
            if len(parts) > 1:
                relative_part = parts[1].lstrip('/')
                return Path(relative_part) if relative_part else Path('.')

        # If no relation found, assume path is already relative to base
        return Path(path_str)

    @staticmethod
    def ensure_relative_path(path: Union[str, Path]) -> Path:
        """
        Ensure path is relative (remove leading slash/drive).

        Args:
            path: Input path

        Returns:
            Relative Path object
        """
        path_obj = Path(str(path).replace('\\', '/'))

        # Remove leading slash
        if path_obj.is_absolute():
            # For Windows, remove drive letter
            parts = path_obj.parts
            if len(parts) > 0 and ':' in parts[0]:
                # Windows drive letter
                return Path(*parts[1:])
            else:
                # Unix absolute path
                return Path(*parts[1:])

        return path_obj

    @staticmethod
    def audio_file_path(video_id: str, filename: str) -> Path:
        """
        Generate standardized audio file path.

        Args:
            video_id: Video identifier
            filename: Audio filename (e.g., 'original.mp3', 'vocals_removed.mp3')

        Returns:
            Standardized audio file path
        """
        return PathManager.join("audio", video_id, filename)

    @staticmethod
    def lyrics_file_path(video_id: str) -> Path:
        """
        Generate standardized lyrics file path.

        Args:
            video_id: Video identifier

        Returns:
            Standardized lyrics file path
        """
        return PathManager.join("audio", video_id, "lyrics.lrc")

    @staticmethod
    def safe_path_split(path: Union[str, Path]) -> tuple[str, str]:
        """
        Safely split path into directory and filename.

        Args:
            path: Path to split

        Returns:
            Tuple of (directory, filename)
        """
        path_obj = PathManager.normalize_path(path)
        return str(path_obj.parent), path_obj.name

    @staticmethod
    def get_file_extension(path: Union[str, Path]) -> str:
        """
        Get file extension from path.

        Args:
            path: File path

        Returns:
            File extension (including dot)
        """
        return Path(path).suffix.lower()


# Convenience functions for common operations
def fix_corrupted_path(corrupted_path: str) -> str:
    """
    Fix corrupted paths that contain invalid escape sequences.
    Common issue: 'data\\audio' becomes 'data\x07udio' due to \\a being interpreted as ASCII bell.

    Args:
        corrupted_path: Path that may contain corrupted escape sequences

    Returns:
        Fixed path string
    """
    # Handle common corrupted patterns
    fixes = {
        'dataudio': 'data/audio',  # \a becomes bell character
        'data\x07udio': 'data/audio',  # explicit bell character
        'data\audio': 'data/audio',  # single backslash case
    }

    fixed_path = corrupted_path
    for corrupted, correct in fixes.items():
        fixed_path = fixed_path.replace(corrupted, correct)

    # Convert all backslashes to forward slashes for consistency
    fixed_path = fixed_path.replace('\\', '/')

    return fixed_path


def normalize_storage_path(path: Union[str, Path]) -> str:
    """
    Normalize a storage path for cross-platform use.
    Returns string representation with forward slashes.

    Args:
        path: Input path

    Returns:
        Normalized path string
    """
    normalized = PathManager.normalize_path(path)
    return str(normalized).replace('\\', '/')


def build_relative_path(*parts: Union[str, Path]) -> str:
    """
    Build relative path from parts, ensuring forward slashes.

    Args:
        *parts: Path components

    Returns:
        Relative path string with forward slashes
    """
    joined = PathManager.join(*parts)
    relative = PathManager.ensure_relative_path(joined)
    return str(relative).replace('\\', '/')