import streamlit as st
import zipfile
import io
import json
import time
from typing import List, Tuple, Optional, Dict, Any
from services.streamlitClient.api.api_client import get_song_assets
from services.streamlitClient.api.helpers import seconds_to_mmss, validate_video_id
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="נגן קריוקי", page_icon="🎤", layout="wide")

logger.info("Karaoke player page accessed")
logger.debug("Karaoke player: Initializing player page")

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
def load_assets(vid: str) -> Tuple[Optional[bytes], Optional[List[Dict[str, Any]]]]:
    """
    Load and extract karaoke assets from ZIP file.

    Args:
        vid: YouTube video ID

    Returns:
        Tuple of (audio_bytes, lyrics_data) or (None, None) if failed
    """
    try:
        logger.info(f"Loading assets for video_id: {vid}")
        zip_content = get_song_assets(vid)
        if not zip_content:
            logger.error(f"Failed to get zip content for video_id: {vid}")
            return None, None

        logger.info(f"Extracting assets from zip for video_id: {vid} ({len(zip_content)} bytes)")
        audio_bytes, lyrics_data = None, None

        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as thezip:
                for filename in thezip.namelist():
                    try:
                        if filename.endswith('.wav'):
                            audio_bytes = thezip.read(filename)
                            logger.info(f"Extracted audio ({len(audio_bytes)} bytes) for {vid}")
                        elif filename.endswith('.json'):
                            lyrics_content = thezip.read(filename).decode('utf-8')
                            lyrics_data = json.loads(lyrics_content)
                            logger.info(f"Extracted JSON lyrics ({len(lyrics_data)} words) for {vid}")
                    except Exception as e:
                        logger.error(f"Error extracting file {filename} for {vid}: {e}")
                        continue

        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file for video_id {vid}: {e}")
            return None, None

        return audio_bytes, lyrics_data

    except Exception as e:
        logger.error(f"Unexpected error loading assets for {vid}: {e}")
        return None, None


try:
    audio_bytes, lyrics_data = load_assets(video_id)
except Exception as e:
    logger.error(f"Error in load_assets function for {video_id}: {e}")
    audio_bytes, lyrics_data = None, None

if not audio_bytes or not lyrics_data:
    logger.critical(f"Critical error loading assets for song '{title}' (video_id: {video_id}). Audio or lyrics JSON is missing.")
    st.error("שגיאה חמורה בטעינת קבצי הקריוקי. ייתכן שההורדה נכשלה.")
    if st.button("חזור לספרייה"):
        st.switch_page("pages/3_🎵_ספריה.py")
    st.stop()

logger.info(f"Successfully loaded assets for '{title}'. Rendering player UI.")

def find_current_word_index(lyrics_data: List[Dict[str, Any]], current_time: float) -> int:
    """
    Find the index of the current word based on the playback time.

    Args:
        lyrics_data: List of word objects with timing
        current_time: Current playback time in seconds

    Returns:
        Index of current word, or -1 if no word is active
    """
    for i, word in enumerate(lyrics_data):
        if word['start'] <= current_time <= word['end']:
            return i
    return -1

def get_lyrics_context(lyrics_data: List[Dict[str, Any]], current_index: int, context_words: int = 10) -> Dict:
    """
    Get context around the current word for display.

    Args:
        lyrics_data: List of word objects
        current_index: Index of current word
        context_words: Number of words to show before and after current word

    Returns:
        Dict with previous, current, and next word groups
    """
    total_words = len(lyrics_data)

    if current_index < 0:
        # No active word, show first few words
        return {
            'previous': [],
            'current': None,
            'next': lyrics_data[:context_words * 2] if lyrics_data else []
        }

    start_idx = max(0, current_index - context_words)
    end_idx = min(total_words, current_index + context_words + 1)

    return {
        'previous': lyrics_data[start_idx:current_index],
        'current': lyrics_data[current_index] if current_index < total_words else None,
        'next': lyrics_data[current_index + 1:end_idx]
    }

def render_lyrics_line(words: List[Dict], current_word: Dict = None, word_type: str = "normal") -> str:
    """
    Render a line of lyrics with appropriate styling.

    Args:
        words: List of word objects to render
        current_word: Currently active word (for highlighting)
        word_type: Type of words ('previous', 'current', 'next')

    Returns:
        HTML string for the lyrics line
    """
    if not words:
        return ""

    html_parts = []
    for word in words:
        word_text = word['word'].strip()
        if word_type == 'previous':
            html_parts.append(f'<span style="color: #888; opacity: 0.7;">{word_text}</span>')
        elif word_type == 'next':
            html_parts.append(f'<span style="color: #333;">{word_text}</span>')
        else:  # normal
            html_parts.append(f'<span>{word_text}</span>')

    return ' '.join(html_parts)

def render_current_word(word: Dict) -> str:
    """Render the currently active word with highlighting."""
    if not word:
        return ""

    word_text = word['word'].strip()
    confidence = word['probability']

    # Color based on confidence
    if confidence > 0.9:
        color = "#00ff00"  # Green for high confidence
    elif confidence > 0.7:
        color = "#ffff00"  # Yellow for medium confidence
    else:
        color = "#ff8800"  # Orange for low confidence

    return f'<span style="color: {color}; font-weight: bold; font-size: 1.2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{word_text}</span>'

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
                st.audio(audio_bytes, format='audio/wav')
            except Exception as e:
                logger.error(f"Error creating audio player for {video_id}: {e}")
                st.error("שגיאה בטעינת נגן האודיו")

            # Initialize karaoke state
            if 'karaoke_active' not in st.session_state:
                st.session_state.karaoke_active = False
                st.session_state.current_time = 0.0
                st.session_state.start_time = None

            # Karaoke controls
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🎤 הפעל קריוקי"):
                    st.session_state.karaoke_active = True
                    st.session_state.start_time = time.time()
                    st.rerun()

            with col2:
                if st.button("⏸️ עצור"):
                    st.session_state.karaoke_active = False
                    st.session_state.start_time = None
                    st.rerun()

            with col3:
                if st.button("🔄 איפוס"):
                    st.session_state.karaoke_active = False
                    st.session_state.current_time = 0.0
                    st.session_state.start_time = None
                    st.rerun()

            if st.session_state.karaoke_active:
                st.success("🎤 מצב קריוקי פעיל - מילים יודגשו בזמן אמת!")
            else:
                st.info("💡 לחץ 'הפעל קריוקי' כדי לראות הדגשת מילים דינמית")

    except Exception as e:
        logger.error(f"Error rendering left column for {video_id}: {e}")
        st.error("שגיאה בטעינת פרטי השיר")

# Right Column: Dynamic Karaoke Lyrics Display
with main_cols[1]:
    try:
        st.subheader("🎤 מילות השיר - מצב קריוקי")

        if not lyrics_data:
            logger.warning(f"No lyrics data found for song '{title}'.")
            st.warning("לא נמצאו מילות שיר בקובץ ה-JSON.")
        else:
            logger.info(f"Displaying karaoke for {len(lyrics_data)} words for '{title}'.")

            # Update current time if karaoke is active
            if st.session_state.karaoke_active and st.session_state.start_time:
                st.session_state.current_time = time.time() - st.session_state.start_time

            # Find current word
            current_word_index = find_current_word_index(lyrics_data, st.session_state.current_time)
            context = get_lyrics_context(lyrics_data, current_word_index, context_words=8)

            # Lyrics display container
            with st.container(height=500, border=True):
                # Show current time and progress
                if st.session_state.karaoke_active:
                    time_str = seconds_to_mmss(st.session_state.current_time)
                    progress = min(st.session_state.current_time / (lyrics_data[-1]['end'] + 5), 1.0) if lyrics_data else 0
                    st.progress(progress, text=f"זמן: {time_str}")

                # Previous words (grayed out)
                if context['previous']:
                    previous_html = render_lyrics_line(context['previous'], word_type='previous')
                    st.markdown(f'<div style="text-align: center; margin: 20px 0; font-size: 1.1em;">{previous_html}</div>',
                              unsafe_allow_html=True)

                # Current word (highlighted)
                if context['current']:
                    current_html = render_current_word(context['current'])
                    confidence = context['current']['probability']
                    st.markdown(f'<div style="text-align: center; margin: 30px 0; font-size: 2em;">{current_html}</div>',
                              unsafe_allow_html=True)

                    # Show word timing info
                    start_time = seconds_to_mmss(context['current']['start'])
                    end_time = seconds_to_mmss(context['current']['end'])
                    st.caption(f"⏱️ {start_time} - {end_time} | 🎯 ביטחון: {confidence:.1%}")
                else:
                    # No current word - show waiting message
                    if st.session_state.karaoke_active:
                        if st.session_state.current_time < lyrics_data[0]['start']:
                            st.markdown('<div style="text-align: center; margin: 30px 0; font-size: 1.5em; color: #666;">⏳ מחכה להתחלת השיר...</div>',
                                      unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="text-align: center; margin: 30px 0; font-size: 1.5em; color: #666;">🎵 השיר הסתיים</div>',
                                      unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="text-align: center; margin: 30px 0; font-size: 1.2em; color: #888;">▶️ לחץ "הפעל קריוקי" כדי להתחיל</div>',
                                  unsafe_allow_html=True)

                # Next words (normal color)
                if context['next']:
                    next_html = render_lyrics_line(context['next'], word_type='next')
                    st.markdown(f'<div style="text-align: center; margin: 20px 0; font-size: 1.1em;">{next_html}</div>',
                              unsafe_allow_html=True)

                # Auto-refresh when karaoke is active
                if st.session_state.karaoke_active:
                    time.sleep(0.1)  # Small delay to prevent too frequent updates
                    st.rerun()

    except Exception as e:
        logger.error(f"Error rendering karaoke lyrics for {video_id}: {e}")
        st.error("שגיאה בטעינת מצב הקריוקי")

if st.button("חזור לספריית השירים"):
    logger.info(f"User clicked 'Back to Library' from player page for song '{title}'.")
    try:
        st.switch_page("pages/3_🎵_ספריה.py")
    except Exception as e:
        logger.error(f"Error switching to library page: {e}")
        st.error("שגיאה בחזרה לספרייה")
