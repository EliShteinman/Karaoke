import streamlit as st
import zipfile
import io
from services.streamlitClient.api.api_client import get_song_assets
from services.streamlitClient.api.lrc_parser import parse_lrc, LrcLine
from services.streamlitClient.api.helpers import seconds_to_mmss
from shared.utils import Logger

logger = Logger.get_logger()

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
logger.info(f"Karaoke player page loaded for song: '{title}' (video_id: {video_id})")

@st.cache_data(show_spinner="מוריד את קבצי השיר...")
def load_assets(vid):
    logger.info(f"Loading assets for video_id: {vid}")
    zip_content = get_song_assets(vid)
    if not zip_content:
        logger.error(f"Failed to get zip content for video_id: {vid}")
        return None, None
    
    logger.info(f"Extracting assets from zip for video_id: {vid}")
    audio_bytes, lrc_text = None, None
    with zipfile.ZipFile(io.BytesIO(zip_content)) as thezip:
        for filename in thezip.namelist():
            if filename.endswith('.mp3'):
                audio_bytes = thezip.read(filename)
                logger.info(f"Extracted audio ({len(audio_bytes)} bytes) for {vid}")
            elif filename.endswith('.lrc'):
                lrc_text = thezip.read(filename).decode('utf-8')
                logger.info(f"Extracted LRC text ({len(lrc_text)} chars) for {vid}")
    return audio_bytes, lrc_text

audio_bytes, lrc_text = load_assets(video_id)

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
    with st.container(border=True):
        st.image(song.get('thumbnail'), use_column_width=True)
        st.subheader(song.get('title', 'ללא כותרת'))
        st.markdown(f"**אמן:** {song.get('artist', 'לא ידוע')}")
        st.markdown(f"**משך:** {seconds_to_mmss(song.get('duration'))}")
        st.audio(audio_bytes, format='audio/mp3')
        st.warning("**הערה:** סנכרון והדגשת כתוביות בזמן אמת אינו נתמך כרגע.", icon="⚠️")

# Right Column: Lyrics Display
with main_cols[1]:
    st.subheader("מילות השיר")
    lyrics_lines: list[LrcLine] = parse_lrc(lrc_text)
    
    if not lyrics_lines:
        logger.warning(f"No lyric lines found after parsing LRC for song '{title}'.")
        st.warning("לא נמצאו מילות שיר בקובץ הכתוביות.")
    else:
        logger.info(f"Displaying {len(lyrics_lines)} lyric lines for '{title}'.")
        # Display lyrics in a scrollable container
        with st.container(height=500, border=True):
            for line in lyrics_lines:
                st.markdown(f"`{seconds_to_mmss(line.timestamp)}` {line.text}")

if st.button("חזור לספריית השירים"):
    logger.info(f"User clicked 'Back to Library' from player page for song '{title}'.")
    st.switch_page("pages/3_🎵_ספריה.py")
