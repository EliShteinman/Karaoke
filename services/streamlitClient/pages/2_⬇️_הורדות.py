import streamlit as st
import time
from typing import List, Dict, Any
from services.streamlitClient.api.api_client import get_songs_library
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="הורדות ועיבוד", page_icon="⬇️")
st.title("⬇️ שירים בתהליך עיבוד")

logger.info("Downloads page loaded")
logger.debug("Downloads page: Initializing downloads page components")

def get_status_color(status: str) -> str:
    """Get color for status indicator"""
    status_colors = {
        'ready': '🟢',
        'completed': '🟢',
        'processing': '🟡',
        'downloading': '🟠',
        'failed': '🔴',
        'error': '🔴',
        'queued': '🔵'
    }
    return status_colors.get(status.lower(), '⚪')

def get_progress_percentage(progress: Dict[str, Any]) -> float:
    """Calculate overall progress percentage"""
    if not progress:
        return 0.0

    steps = ['download', 'audio_processing', 'transcription']
    completed_steps = sum(1 for step in steps if progress.get(step, False))
    return (completed_steps / len(steps)) * 100

def render_detailed_progress(progress: Dict[str, Any]) -> None:
    """Render detailed progress information"""
    if not progress:
        st.write("❓ מידע התקדמות לא זמין")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        if progress.get('download', False):
            st.success("✅ הורדה הושלמה")
        else:
            st.warning("⏳ מוריד מיוטיוב...")

    with col2:
        if progress.get('audio_processing', False):
            st.success("✅ עיבוד אודיו הושלם")
        elif progress.get('download', False):
            st.info("🔄 מעבד אודיו...")
        else:
            st.write("⏸️ ממתין לסיום הורדה")

    with col3:
        if progress.get('transcription', False):
            st.success("✅ תמלול הושלם")
        elif progress.get('audio_processing', False):
            st.info("🔄 מתמלל...")
        else:
            st.write("⏸️ ממתין לעיבוד אודיו")

    # Overall progress bar
    percentage = get_progress_percentage(progress)
    st.progress(percentage / 100)
    st.caption(f"התקדמות כללית: {percentage:.0f}%")

@st.cache_data(ttl=15, show_spinner=False)  # Shorter cache for real-time updates
def get_processing_songs_with_forced_refresh() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Force refresh of songs data to get latest processing status"""
    logger.info("Force refreshing songs data from API...")
    all_songs = get_songs_library()

    # Filter to show only processing songs using new progress data
    processing_songs = []
    for song in all_songs:
        progress = song.get('progress', {})
        files_ready = progress.get('files_ready', False) if progress else song.get('files_ready', True)
        status = song.get('status', '')

        # Include songs that are not ready and not failed
        if not files_ready and status.lower() not in ['failed', 'error']:
            processing_songs.append(song)

    logger.info(f"Found {len(processing_songs)} processing songs out of {len(all_songs)} total")
    return processing_songs, all_songs

# Refresh controls
col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    if st.button("🔄 רענן מאולץ", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    auto_refresh = st.checkbox("🔄 רענון אוטומטי", value=True, help="רענון אוטומטי כל 10 שניות")

with col3:
    show_details = st.checkbox("📊 הצג פרטי התקדמות", value=True)

# Fetch processing songs with forced refresh
with st.spinner("טוען שירים בעיבוד..."):
    processing_songs, all_songs = get_processing_songs_with_forced_refresh()

if not processing_songs:
    st.info("🎉 אין כרגע שירים בתהליך עיבוד!")
    st.markdown("כל השירים מוכנים או שאין שירים ברשימה.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 חפש שירים חדשים", width='stretch'):
            st.switch_page("pages/1_🔍_חיפוש.py")
    with col2:
        if st.button("🎵 עבור לספרייה", width='stretch'):
            st.switch_page("pages/3_🎵_ספריה.py")
else:
    st.markdown(f"**נמצאו {len(processing_songs)} שירים בתהליך עיבוד:**")

    for song in processing_songs:
        video_id = song.get('video_id', '')

        with st.container(border=True):
            col1, col2 = st.columns([1, 3])

            with col1:
                try:
                    if song.get('thumbnail'):
                        st.image(song['thumbnail'], width='stretch')
                    else:
                        st.write("🎵")
                except Exception as e:
                    logger.warning(f"Error displaying thumbnail for {video_id}: {e}")
                    st.write("🎵")

            with col2:
                # Title with status indicator
                status = song.get('status', 'לא ידוע')
                status_indicator = get_status_color(status)
                st.subheader(f"{status_indicator} {song.get('title', 'שיר לא ידוע')}")

                # Basic info
                artist = song.get('artist', 'לא ידוע')
                duration = song.get('duration', 0)
                duration_str = f"{duration//60}:{duration%60:02d}" if duration > 0 else "לא ידוע"
                st.caption(f"אמן: {artist} | משך: {duration_str}")

                # Show creation time if available
                if song.get('created_at'):
                    try:
                        from datetime import datetime
                        created_time = datetime.fromisoformat(song['created_at'].replace('Z', '+00:00'))
                        st.caption(f"התחיל: {created_time.strftime('%d/%m/%Y %H:%M')}")
                    except:
                        st.caption(f"התחיל: {song.get('created_at')}")

                # Enhanced status display with progress
                progress = song.get('progress', {})
                if progress:
                    percentage = get_progress_percentage(progress)

                    # Status with progress percentage
                    if status == 'processing':
                        st.markdown(f"🔄 **סטטוס:** בתהליך עיבוד ({percentage:.0f}%)")
                    elif status == 'downloading':
                        st.markdown(f"📥 **סטטוס:** מוריד מיוטיוב ({percentage:.0f}%)")
                    elif status == 'queued':
                        st.markdown("⏳ **סטטוס:** ממתין בתור")
                    elif status == 'failed':
                        st.markdown("❌ **סטטוס:** העיבוד נכשל")
                        st.error("תהליך העיבוד נכשל. השיר לא יהיה זמין.")
                    else:
                        st.markdown(f"ℹ️ **סטטוס:** {status} ({percentage:.0f}%)")

                    # Show detailed progress if enabled
                    if show_details:
                        with st.expander("📊 פרטי התקדמות", expanded=True):
                            render_detailed_progress(progress)
                else:
                    # Fallback to old display if no progress data
                    if status == 'processing':
                        st.markdown("🔄 **סטטוס:** בתהליך עיבוד...")
                    elif status == 'queued':
                        st.markdown("⏳ **סטטוס:** ממתין בתור")
                    elif status == 'downloading':
                        st.markdown("📥 **סטטוס:** מוריד מיוטיוב...")
                    elif status == 'failed':
                        st.markdown("❌ **סטטוס:** העיבוד נכשל")
                        st.error("תהליך העיבוד נכשל. השיר לא יהיה זמין.")
                    else:
                        st.markdown(f"ℹ️ **סטטוס:** {status}")

                    if show_details:
                        st.info("מידע התקדמות מפורט לא זמין לשיר זה")

# Instructions
st.markdown("---")
st.markdown("### 💡 מידע שימושי")
st.markdown("""
- הדף מציג שירים שכרגע בתהליך עיבוד (מתוך endpoint `GET /songs`)
- השירים מסוננים לפי `files_ready: false`
- תהליך העיבוד: הורדה מיוטיוב ← עיבוד אודיו ← תמלול וכתוביות
- זמן העיבוד הממוצע: 2-5 דקות לכל שיר
- שירים מוכנים יעברו אוטומטית לדף [🎵 ספריה](/🎵_ספריה)
- הדף מתרענן אוטומטית כל 10 שניות
""")

# Auto-refresh logic for processing songs
if auto_refresh and processing_songs:
    # Auto-refresh every 10 seconds if there are songs in progress
    import time

    if 'last_downloads_refresh' not in st.session_state:
        st.session_state.last_downloads_refresh = time.time()
    elif time.time() - st.session_state.last_downloads_refresh > 10:
        st.session_state.last_downloads_refresh = time.time()
        st.cache_data.clear()
        st.rerun()

    # Show auto-refresh status with countdown
    time_since_refresh = int(time.time() - st.session_state.last_downloads_refresh)
    next_refresh = max(0, 10 - time_since_refresh)
    st.info(f"🔄 רענון אוטומטי פעיל - {len(processing_songs)} שירים בעיבוד | רענון הבא תוך {next_refresh} שניות")

# Debug info
if st.checkbox("🔧 מידע דיבוג"):
    st.json({
        "total_songs_from_api": len(all_songs),
        "processing_songs_count": len(processing_songs),
        "processing_songs": processing_songs
    })