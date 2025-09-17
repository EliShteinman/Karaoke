import streamlit as st
from typing import Union, Optional
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)


def show_youtube_player(video_id: str) -> None:
    """
    Embeds a YouTube player in the Streamlit app using modern st.video component.

    Args:
        video_id: YouTube video ID
    """
    try:
        if not validate_video_id(video_id):
            st.error("מזהה וידאו יוטיוב לא תקין")
            return

        logger.info(f"Displaying YouTube player for video_id: {video_id}")
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        st.video(youtube_url, format="video/mp4", start_time=0)
    except Exception as e:
        logger.error(f"Error displaying YouTube player for video_id {video_id}: {e}")
        st.error(f"שגיאה בהצגת נגן יוטיוב: {e}")


def seconds_to_mmss(seconds: Optional[Union[int, float]]) -> str:
    """
    Converts seconds to a MM:SS format string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted time string in MM:SS format
    """
    try:
        if not isinstance(seconds, (int, float)) or seconds is None:
            logger.warning(f"Invalid type for seconds_to_mmss: {type(seconds)}. Returning '00:00'.")
            return "00:00"

        if seconds < 0:
            logger.warning(f"Negative seconds value: {seconds}. Returning '00:00'.")
            return "00:00"

        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes:02d}:{remaining_seconds:02d}"

    except Exception as e:
        logger.error(f"Error converting seconds to MM:SS format: {e}")
        return "00:00"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB", "500 KB")
    """
    try:
        if not isinstance(size_bytes, (int, float)) or size_bytes < 0:
            logger.warning(f"Invalid file size: {size_bytes}")
            return "0 B"

        if size_bytes == 0:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                if unit == 'B':
                    return f"{int(size_bytes)} {unit}"
                else:
                    return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024

        return f"{size_bytes:.1f} PB"

    except Exception as e:
        logger.error(f"Error formatting file size: {e}")
        return "0 B"


def validate_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.

    Args:
        video_id: YouTube video ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        if not isinstance(video_id, str):
            return False

        # YouTube video IDs are typically 11 characters long
        # and contain alphanumeric characters, hyphens, and underscores
        import re
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        is_valid = bool(re.match(pattern, video_id))

        if not is_valid:
            logger.warning(f"Invalid video ID format: {video_id}")

        return is_valid

    except Exception as e:
        logger.error(f"Error validating video ID {video_id}: {e}")
        return False
