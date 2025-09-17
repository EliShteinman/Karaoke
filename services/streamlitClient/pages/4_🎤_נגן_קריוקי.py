import streamlit as st
import zipfile
import io
from typing import List, Tuple, Optional
from services.streamlitClient.api.api_client import get_song_assets
from services.streamlitClient.api.lrc_parser import parse_lrc, LrcLine
from services.streamlitClient.api.helpers import seconds_to_mmss, validate_video_id
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="נגן קריוקי", page_icon="🎤", layout="wide")

# --- Initial check for a selected song ---
if 'song_to_play' not in st.session_state or not st.session_state['song_to_play']:
    logger.warning("Karaoke player page loaded without a selected song.")
    st.title("לא נבחר שיר")
    st.info("עליך לבחור שיר מספריית השירים כדי להפעיל את הנגן.")
    if st.button("עבור לספרייה"):  # Corrected button text
        logger.info("User clicked 'Go to Library' from player page.")
        st.switch_page("pages/3_🎵_ספריה.py")
    st.stop()

# --- Load song and assets ---
song = st.session_state['song_to_play']
video_id = song.get('video_id')
title = song.get('title', 'N/A')

# Validate video ID
if not video_id or not validate_video_id(video_id):
    logger.error(f"Invalid video ID in player: {video_id}")
    st.error("מזהה הוידאו אינו תקין")
    if st.button("חזור לספרייה"):
        st.switch_page("pages/3_🎵_ספריה.py")
    st.stop()

logger.info(f"Karaoke player page loaded for song: '{title}' (video_id: {video_id})")


@st.cache_data(show_spinner="מוריד את קבצי השיר...")
def load_assets(vid: str) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Load and extract karaoke assets from ZIP file.

    Args:
        vid: YouTube video ID

    Returns:
        Tuple of (audio_bytes, lrc_text) or (None, None) if failed
    """
    try:
        logger.info(f"Loading assets for video_id: {vid}")
        zip_content = get_song_assets(vid)
        if not zip_content:
            logger.error(f"Failed to get zip content for video_id: {vid}")
            return None, None

        logger.info(f"Extracting assets from zip for video_id: {vid} ({len(zip_content)} bytes)")
        audio_bytes, lrc_text = None, None

        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as thezip:
                for filename in thezip.namelist():
                    try:
                        if filename.endswith('.mp3'):
                            audio_bytes = thezip.read(filename)
                            logger.info(f"Extracted audio ({len(audio_bytes)} bytes) for {vid}")
                        elif filename.endswith('.lrc'):
                            lrc_text = thezip.read(filename).decode('utf-8')
                            logger.info(f"Extracted LRC text ({len(lrc_text)} chars) for {vid}")
                    except Exception as e:
                        logger.error(f"Error extracting file {filename} for {vid}: {e}")
                        continue

        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file for video_id {vid}: {e}")
            return None, None

        return audio_bytes, lrc_text

    except Exception as e:
        logger.error(f"Unexpected error loading assets for {vid}: {e}")
        return None, None


try:
    audio_bytes, lrc_text = load_assets(video_id)
except Exception as e:
    logger.error(f"Error in load_assets function for {video_id}: {e}")
    audio_bytes, lrc_text = None, None

if not audio_bytes or not lrc_text:
    logger.critical(f"Critical error loading assets for song '{title}' (video_id: {video_id}). Audio or LRC is missing.")
    st.error("שגיאה חמורה בטעינת קבצי הקריוקי. ייתכן שההורדה נכשלה.")
    if st.button("חזור לספרייה"):
        st.switch_page("pages/3_🎵_ספריה.py")
    st.stop()

logger.info(f"Successfully loaded assets for '{title}'. Rendering player UI.")

# --- Player UI ---
st.title(f"🎤 {song.get('title', 'נגן קריוקי')}")

main_cols = st.columns([2, 3])

# Left Column: Metadata and Audio Player
with main_cols[0]:
    try:
        with st.container(border=True):
            # Display thumbnail
            try:
                st.image(song.get('thumbnail'), use_container_width=True)
            except Exception as e:
                logger.warning(f"Error displaying thumbnail for {video_id}: {e}")
                st.write("🎵")  # Fallback icon

            st.subheader(song.get('title', 'ללא כותרת'))
            st.markdown(f"**אמן:** {song.get('artist', 'לא ידוע')}")

            # Format duration safely
            try:
                duration_str = seconds_to_mmss(song.get('duration'))
                st.markdown(f"**משך:** {duration_str}")
            except Exception as e:
                logger.warning(f"Error formatting duration for {video_id}: {e}")

            # Audio player
            try:
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e:
                logger.error(f"Error creating audio player for {video_id}: {e}")
                st.error("שגיאה בטעינת נגן האודיו")

            st.warning("**הערה:** סנכרון והדגשת כתוביות בזמן אמת אינו נתמך כרגע.", icon="⚠️")

    except Exception as e:
        logger.error(f"Error rendering left column for {video_id}: {e}")
        st.error("שגיאה בטעינת פרטי השיר")

# Right Column: Lyrics Display
with main_cols[1]:
    try:
        st.subheader("מילות השיר")
        lyrics_lines: List[LrcLine] = parse_lrc(lrc_text)

        if not lyrics_lines:
            logger.warning(f"No lyric lines found after parsing LRC for song '{title}'.")
            st.warning("לא נמצאו מילות שיר בקובץ הכתוביות.")
        else:
            logger.info(f"Displaying {len(lyrics_lines)} lyric lines for '{title}'.")
            # Display lyrics in a scrollable container
            with st.container(height=500, border=True):
                for line in lyrics_lines:
                    try:
                        timestamp_str = seconds_to_mmss(line.timestamp)
                        st.markdown(f"`{timestamp_str}` {line.text}")
                    except Exception as e:
                        logger.warning(f"Error displaying lyric line: {e}")
                        st.markdown(f"`--:--` {line.text}")

    except Exception as e:
        logger.error(f"Error rendering lyrics for {video_id}: {e}")
        st.error("שגיאה בטעינת הכתוביות")

if st.button("חזור לספריית השירים"):
    logger.info(f"User clicked 'Back to Library' from player page for song '{title}'.")
    try:
        st.switch_page("pages/3_🎵_ספריה.py")
    except Exception as e:
        logger.error(f"Error switching to library page: {e}")
        st.error("שגיאה בחזרה לספרייה")
