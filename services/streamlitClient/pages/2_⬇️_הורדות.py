import streamlit as st
import time
from services.streamlitClient.api.api_client import get_songs_library
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="הורדות ועיבוד", page_icon="⬇️")
st.title("⬇️ שירים בתהליך עיבוד")

# Refresh controls
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 רענן", width='stretch'):
        st.cache_data.clear()
        st.rerun()

with col2:
    auto_refresh = st.checkbox("רענון אוטומטי (כל 10 שניות)", value=True)

# Auto-refresh logic
if auto_refresh:
    # Show countdown and auto-refresh
    placeholder = st.empty()
    for i in range(10, 0, -1):
        placeholder.info(f"⏱️ רענון אוטומטי פעיל - רענון תוך {i} שניות...")
        time.sleep(1)
    placeholder.empty()
    st.cache_data.clear()
    st.rerun()

# Fetch all songs from API
logger.info("Fetching all songs from API to find processing ones...")
with st.spinner("טוען שירים..."):
    all_songs = get_songs_library()

# Filter to show only processing songs (files_ready = false)
processing_songs = [
    song for song in all_songs
    if not song.get('files_ready', True)  # Show songs where files are NOT ready
]

logger.info(f"Found {len(processing_songs)} processing songs out of {len(all_songs)} total songs")

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
                st.subheader(song.get('title', 'שיר לא ידוע'))

                # Basic info
                artist = song.get('artist', 'לא ידוע')
                duration = song.get('duration', 0)
                duration_str = f"{duration//60}:{duration%60:02d}" if duration > 0 else "לא ידוע"
                st.caption(f"אמן: {artist} | משך: {duration_str}")

                # Display status from the song data
                status = song.get('status', 'לא ידוע')
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

                # Show creation time if available
                if song.get('created_at'):
                    try:
                        from datetime import datetime
                        created_time = datetime.fromisoformat(song['created_at'].replace('Z', '+00:00'))
                        st.caption(f"התחיל: {created_time.strftime('%d/%m/%Y %H:%M')}")
                    except:
                        st.caption(f"התחיל: {song.get('created_at')}")

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

# Debug info
if st.checkbox("🔧 מידע דיבוג"):
    st.json({
        "total_songs_from_api": len(all_songs),
        "processing_songs_count": len(processing_songs),
        "processing_songs": processing_songs
    })