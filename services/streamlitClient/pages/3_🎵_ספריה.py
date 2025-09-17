import streamlit as st
from typing import List, Dict, Any
from services.streamlitClient.api.api_client import get_songs_library
from services.streamlitClient.api.helpers import seconds_to_mmss, validate_video_id
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="ספריית השירים", page_icon="🎵")
st.title("🎵 ספריית השירים")

logger.info("Library page loaded.")
logger.debug("Library page: Initializing library page components")

def get_status_color(status: str) -> str:
    """Get color for status indicator"""
    status_colors = {
        'ready': '🟢',
        'completed': '🟢',
        'processing': '🟡',
        'downloading': '🟠',
        'failed': '🔴',
        'error': '🔴'
    }
    return status_colors.get(status.lower(), '⚪')

def get_progress_percentage(progress: Dict[str, Any]) -> float:
    """Calculate overall progress percentage"""
    if not progress:
        return 0.0

    steps = ['download', 'audio_processing', 'transcription']
    completed_steps = sum(1 for step in steps if progress.get(step, False))
    return (completed_steps / len(steps)) * 100

def render_progress_bar(progress: Dict[str, Any]) -> None:
    """Render detailed progress bar with status indicators"""
    if not progress:
        st.write("❓ לא זמין")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        icon = "✅" if progress.get('download', False) else "⏳"
        st.write(f"{icon} הורדה")

    with col2:
        icon = "✅" if progress.get('audio_processing', False) else "⏳"
        st.write(f"{icon} עיבוד אודיו")

    with col3:
        icon = "✅" if progress.get('transcription', False) else "⏳"
        st.write(f"{icon} תמלול")

    with col4:
        if progress.get('files_ready', False):
            st.write("🎵 מוכן!")
        else:
            percentage = get_progress_percentage(progress)
            st.write(f"⏳ {percentage:.0f}%")

@st.cache_data(ttl=30, show_spinner=True)  # Reduced TTL for more frequent updates
def get_all_songs_with_progress():
    """Get all songs from the library with progress information"""
    try:
        all_songs = get_songs_library()
        logger.info(f"Fetched {len(all_songs)} songs from library")
        return all_songs
    except Exception as e:
        logger.error(f"Error fetching songs: {e}")
        return []

# Refresh controls and status filters
col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    if st.button("🔄 רענן", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    # Auto-refresh toggle for processing songs
    auto_refresh = st.checkbox("🔄 רענון אוטומטי", value=True, help="רענון אוטומטי לשירים בעיבוד")

with col3:
    # Status filter
    status_filter = st.selectbox(
        "📊 סנן לפי סטטוס:",
        options=["הכל", "מוכן", "בעיבוד", "הורדה", "כשל"],
        index=0
    )

# Load all songs with progress
with st.spinner("טוען את כל השירים..."):
    all_songs = get_all_songs_with_progress()

if not all_songs:
    logger.info("No songs found in library.")
    st.info("אין שירים בספרייה. התחל בחיפוש והורדה של שירים חדשים.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 חפש שירים חדשים", use_container_width=True):
            logger.info("User navigated to search from empty library.")
            st.switch_page("pages/1_🔍_חיפוש.py")

    with col2:
        if st.button("⬇️ עבור להורדות", use_container_width=True):
            logger.info("User navigated to downloads from empty library.")
            st.switch_page("pages/2_⬇️_הורדות.py")
else:
    # Filter by status
    if status_filter == "מוכן":
        filtered_by_status = [song for song in all_songs if song.get('progress', {}).get('files_ready', False)]
    elif status_filter == "בעיבוד":
        filtered_by_status = [song for song in all_songs if not song.get('progress', {}).get('files_ready', False) and song.get('status', '') not in ['failed', 'error']]
    elif status_filter == "הורדה":
        filtered_by_status = [song for song in all_songs if song.get('status', '').lower() in ['downloading']]
    elif status_filter == "כשל":
        filtered_by_status = [song for song in all_songs if song.get('status', '').lower() in ['failed', 'error']]
    else:  # "הכל"
        filtered_by_status = all_songs

    # Statistics
    ready_count = len([s for s in all_songs if s.get('progress', {}).get('files_ready', False)])
    processing_count = len([s for s in all_songs if not s.get('progress', {}).get('files_ready', False) and s.get('status', '') not in ['failed', 'error']])
    failed_count = len([s for s in all_songs if s.get('status', '').lower() in ['failed', 'error']])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎵 מוכנים", ready_count)
    with col2:
        st.metric("⏳ בעיבוד", processing_count)
    with col3:
        st.metric("🔴 כשלים", failed_count)
    with col4:
        st.metric("📊 סה\"כ", len(all_songs))

    # Search functionality
    search_term = st.text_input("🔍 חפש בספרייה:", placeholder="הקלד שם שיר או אמן...")

    # Filter songs based on search
    if search_term:
        filtered_songs = [
            song for song in filtered_by_status
            if search_term.lower() in song.get('title', '').lower() or
               search_term.lower() in song.get('artist', '').lower()
        ]
        logger.info(f"Filtered library to {len(filtered_songs)} songs for search '{search_term}'")
    else:
        filtered_songs = filtered_by_status

    st.markdown(f"**מציג {len(filtered_songs)} מתוך {len(all_songs)} שירים**")

    if not filtered_songs and search_term:
        st.info(f"לא נמצאו שירים המכילים '{search_term}'")

    # Display songs in a 2-column grid
    cols = st.columns(2)
    for i, song in enumerate(filtered_songs):
        try:
            video_id = song.get('video_id')
            if not video_id or not validate_video_id(video_id):
                logger.warning(f"Invalid video ID in library song {i}: {video_id}")
                continue

            col = cols[i % 2]
            with col:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        try:
                            st.image(song.get('thumbnail'), use_container_width=True)
                        except Exception as e:
                            logger.warning(f"Error displaying thumbnail for {video_id}: {e}")
                            st.write("🎵")  # Fallback icon

                    with col2:
                        # Title with status indicator
                        status = song.get('status', '')
                        status_indicator = get_status_color(status)
                        st.subheader(f"{status_indicator} {song.get('title', 'ללא כותרת')}")

                        try:
                            duration_str = seconds_to_mmss(song.get('duration'))
                            st.caption(f"אמן: {song.get('artist', 'לא ידוע')} | משך: {duration_str}")
                        except Exception as e:
                            logger.warning(f"Error formatting duration for {video_id}: {e}")
                            st.caption(f"אמן: {song.get('artist', 'לא ידוע')}")

                        # Show creation date if available
                        if song.get('created_at'):
                            try:
                                from datetime import datetime
                                created_time = datetime.fromisoformat(song['created_at'].replace('Z', '+00:00'))
                                st.caption(f"הורד: {created_time.strftime('%d/%m/%Y %H:%M')}")
                            except:
                                st.caption(f"הורד: {song.get('created_at', 'לא ידוע')}")
                        else:
                            st.caption("תאריך לא ידוע")

                    # Progress section
                    progress = song.get('progress', {})
                    if progress:
                        with st.expander("📊 התקדמות עיבוד", expanded=not progress.get('files_ready', False)):
                            render_progress_bar(progress)

                    # Action button based on status
                    files_ready = progress.get('files_ready', False) if progress else song.get('files_ready', False)

                    if files_ready:
                        button_text = "▶️ הפעל קריוקי"
                        button_type = "primary"
                        disabled = False
                    elif status.lower() in ['failed', 'error']:
                        button_text = "🔄 נסה שוב"
                        button_type = "secondary"
                        disabled = True  # For now, disable retry functionality
                    else:
                        button_text = f"⏳ בעיבוד ({get_progress_percentage(progress):.0f}%)"
                        button_type = "secondary"
                        disabled = True

                    if st.button(button_text, key=f"action_{video_id}", use_container_width=True, type=button_type, disabled=disabled):
                        if files_ready:
                            try:
                                logger.info(f"User clicked 'Play Karaoke' for song: '{song.get('title', 'N/A')}' (video_id: {video_id})")
                                # Set the song to be played and switch to the player page
                                st.session_state['song_to_play'] = song
                                st.switch_page("pages/4_🎤_נגן_קריוקי.py")
                            except Exception as e:
                                logger.error(f"Error starting karaoke for {video_id}: {e}")
                                st.error("שגיאה בהפעלת הקריוקי")

        except Exception as e:
            logger.error(f"Error processing library song {i}: {e}")
            continue

    # Auto-refresh logic for processing songs
    if auto_refresh:
        processing_songs = [s for s in all_songs if not s.get('progress', {}).get('files_ready', False) and s.get('status', '') not in ['failed', 'error']]
        if processing_songs:
            # Auto-refresh every 15 seconds if there are songs in progress
            import time
            if 'last_auto_refresh' not in st.session_state:
                st.session_state.last_auto_refresh = time.time()
            elif time.time() - st.session_state.last_auto_refresh > 15:
                st.session_state.last_auto_refresh = time.time()
                st.cache_data.clear()
                st.rerun()

            # Show auto-refresh status
            st.info(f"🔄 רענון אוטומטי פעיל - {len(processing_songs)} שירים בעיבוד")
