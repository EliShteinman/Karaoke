import streamlit as st
import zipfile
import io
from utils.api_client import get_song_assets
from utils.lrc_parser import parse_lrc, LrcLine
from utils.helpers import seconds_to_mmss

st.set_page_config(page_title="נגן קריוקי", page_icon="🎤", layout="wide")

# --- Initial check for a selected song ---
if 'song_to_play' not in st.session_state or not st.session_state['song_to_play']:
    st.title("לא נבחר שיר")
    st.info("עליך לבחור שיר מספריית השירים כדי להפעיל את הנגן.")
    if st.button("Перейти לספרייה"):  # Corrected button text
        st.switch_page("pages/3_🎵_ספריה.py")
    st.stop()

# --- Load song and assets ---
song = st.session_state['song_to_play']
video_id = song.get('video_id')

@st.cache_data(show_spinner="מוריד את קבצי השיר...")
def load_assets(vid):
    zip_content = get_song_assets(vid)
    if not zip_content:
        return None, None
    
    audio_bytes, lrc_text = None, None
    with zipfile.ZipFile(io.BytesIO(zip_content)) as thezip:
        for filename in thezip.namelist():
            if filename.endswith('.mp3'):
                audio_bytes = thezip.read(filename)
            elif filename.endswith('.lrc'):
                lrc_text = thezip.read(filename).decode('utf-8')
    return audio_bytes, lrc_text

audio_bytes, lrc_text = load_assets(video_id)

if not audio_bytes or not lrc_text:
    st.error("שגיאה חמורה בטעינת קבצי הקריוקי. ייתכן שההורדה נכשלה.")
    st.button("חזור לספרייה")
    st.stop()

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
        st.warning("לא נמצאו מילות שיר בקובץ הכתוביות.")
    else:
        # Display lyrics in a scrollable container
        with st.container(height=500, border=True):
            for line in lyrics_lines:
                st.markdown(f"`{seconds_to_mmss(line.timestamp)}` {line.text}")

if st.button("חזור לספריית השירים"):
    st.switch_page("pages/3_🎵_ספריה.py")
