"""
LRC file generator service
Creates LRC files with proper timing and metadata
Uses shared file storage for consistency
"""
import os
from typing import List

from shared.storage.file_storage import create_file_manager
from shared.utils.logger import Logger

from services.transcriptionService.app.models import TranscriptionSegment, LRCMetadata
from services.transcriptionService.app.services.text_processor import clean_text


logger = Logger.get_logger(__name__)


def format_lrc_timestamp(seconds: float) -> str:
    """
    Format timestamp for LRC format (mm:ss.xx)

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"


def create_lrc_file(
    segments: List[TranscriptionSegment],
    metadata: LRCMetadata,
    output_path: str
) -> str:
    """
    Create LRC file with proper timing and metadata using shared file storage

    Args:
        segments: List of transcription segments with timing
        metadata: LRC metadata (artist, title, album)
        output_path: Output file path

    Returns:
        Path to created LRC file

    Raises:
        Exception: If file creation fails
    """
    try:
        logger.debug(f"Creating LRC file at: {output_path}")

        # Initialize shared file manager
        file_manager = create_file_manager(
            storage_type="volume",
            base_path=os.getenv("SHARED_STORAGE_PATH", "/shared")
        )

        # Build LRC content
        lrc_content = []

        # Add metadata headers
        lrc_content.append(f"[ar:{metadata.artist}]")
        lrc_content.append(f"[ti:{metadata.title}]")
        lrc_content.append(f"[al:{metadata.album}]")
        lrc_content.append(f"[by:Karaoke AI System]")
        lrc_content.append("")

        # Add timestamped lyrics
        for segment in segments:
            start_time = format_lrc_timestamp(segment.start)
            cleaned_text = clean_text(segment.text)
            lrc_content.append(f"[{start_time}]{cleaned_text}")

        # Join content and save using shared file manager
        lrc_text = "\n".join(lrc_content)

        # Extract video_id from output path for file manager
        # Expected path format: /shared/audio/{video_id}/lyrics.lrc
        path_parts = output_path.split('/')
        video_id = None
        for i, part in enumerate(path_parts):
            if part == "audio" and i + 1 < len(path_parts):
                video_id = path_parts[i + 1]
                break

        if not video_id:
            logger.error(f"Could not extract video_id from output path: {output_path}")
            raise ValueError(f"Invalid output path format: {output_path}")

        # Save using shared file manager
        actual_path = file_manager.save_lyrics_file(video_id, lrc_text)

        logger.info(f"Successfully created LRC file: {actual_path}")
        return actual_path

    except Exception as e:
        logger.error(f"Failed to create LRC file at {output_path}. Error: {e}")
        logger.error(f"LRC creation error details: {str(e)}")
        raise