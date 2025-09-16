import streamlit as st

def show_youtube_player(video_id: str):
    """Embeds a YouTube player in the Streamlit app."""
    st.video(f"https://www.youtube.com/watch?v={video_id}")

def seconds_to_mmss(seconds: int) -> str:
    """Converts seconds to a MM:SS format string."""
    if not isinstance(seconds, (int, float)):
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"
