import streamlit as st
from shared.utils import Logger

logger = Logger.get_logger()

def show_youtube_player(video_id: str):
    """Embeds a YouTube player in the Streamlit app."""
    logger.info(f"Displaying YouTube player for video_id: {video_id}")
    st.video(f"https://www.youtube.com/watch?v={video_id}")

def seconds_to_mmss(seconds: int) -> str:
    """Converts seconds to a MM:SS format string."""
    if not isinstance(seconds, (int, float)):
        logger.warning(f"Invalid type for seconds_to_mmss: {type(seconds)}. Returning '00:00'.")
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"
