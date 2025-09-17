"""
LRC file generator service
Creates LRC files with proper timing and metadata
Uses shared file storage for consistency
"""
from typing import List

from shared.storage.file_storage import create_file_manager
from shared.utils.logger import Logger

from services.transcriptionService.app.models import TranscriptionSegment, LRCMetadata
from services.transcriptionService.app.services.text_processor import clean_text
from services.transcriptionService.app.services.config import TranscriptionServiceConfig


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
        logger.info(f"Starting LRC file creation process for {len(segments)} segments")
        logger.debug(f"Target output path: {output_path}")
        logger.debug(f"Metadata: Artist='{metadata.artist}', Title='{metadata.title}', Album='{metadata.album}'")

        # Initialize shared file manager using configuration
        config = TranscriptionServiceConfig()
        logger.debug(f"Using storage base path: {config.storage_base_path}")
        file_manager = create_file_manager(
            storage_type="volume",
            base_path=config.storage_base_path
        )

        # Build LRC content
        lrc_content = []

        # Add metadata headers
        logger.debug("Adding LRC metadata headers")
        lrc_content.append(f"[ar:{metadata.artist}]")
        lrc_content.append(f"[ti:{metadata.title}]")
        lrc_content.append(f"[al:{metadata.album}]")
        lrc_content.append(f"[by:Karaoke AI System]")
        lrc_content.append("")

        # Add timestamped lyrics
        logger.debug(f"Processing {len(segments)} segments for LRC timestamps")
        for i, segment in enumerate(segments):
            start_time = format_lrc_timestamp(segment.start)
            cleaned_text = clean_text(segment.text)
            lrc_content.append(f"[{start_time}]{cleaned_text}")

            if i % 20 == 0:  # Log every 20th segment to avoid spam
                logger.debug(f"Processed LRC segment {i + 1}/{len(segments)}: [{start_time}] {cleaned_text[:50]}{'...' if len(cleaned_text) > 50 else ''}")

        # Join content and save using shared file manager
        lrc_text = "\n".join(lrc_content)
        logger.debug(f"Generated LRC content with {len(lrc_text)} characters")

        # Extract video_id from output path for file manager
        # Expected path format: /shared/audio/{video_id}/lyrics.lrc
        from pathlib import Path
        path_obj = Path(output_path)
        path_parts = path_obj.parts
        video_id = None
        for i, part in enumerate(path_parts):
            if part == "audio" and i + 1 < len(path_parts):
                video_id = path_parts[i + 1]
                break

        if not video_id:
            logger.error(f"Could not extract video_id from output path: {output_path}")
            logger.debug(f"Path parts analysis: {path_parts}")
            raise ValueError(f"Invalid output path format: {output_path}")

        logger.debug(f"Extracted video_id: {video_id}")

        # Save using shared file manager
        logger.debug(f"Saving LRC file using shared file manager for video_id: {video_id}")
        actual_path = file_manager.save_lyrics_file(video_id, lrc_text)

        logger.info(f"Successfully created LRC file at: {actual_path}")
        logger.debug(f"LRC file contains {len(segments)} timestamped segments")
        return actual_path

    except Exception as e:
        logger.error(f"Failed to create LRC file at {output_path}. Error: {e}")
        logger.debug(f"LRC creation error details: {str(e)}")
        raise