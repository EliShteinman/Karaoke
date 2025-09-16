import streamlit as st
import time
from typing import Dict, Any
from services.streamlitClient.api.api_client import get_song_status
from services.streamlitClient.config import StreamlitConfig
from services.streamlitClient.api.helpers import validate_video_id

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="מעקב הורדות", page_icon="⬇️")
st.title("⬇️ מעקב אחר התקדמות ההורדות")

if 'download_requests' not in st.session_state:
    st.session_state['download_requests'] = {}

downloading_songs = st.session_state.get('download_requests', {})

logger.info(f"Downloads page loaded. Tracking {len(downloading_songs)} songs.")

if not downloading_songs:
    st.info("אין כרגע שירים בתהליך הורדה. ניתן להוסיף שירים מהדף 'חיפוש והורדה'.")
else:
    st.markdown("הסטטוסים מתעדכנים אוטומטית כל 5 שניות.")
    
    # Create a copy of items to iterate over, to allow modification during iteration
    for video_id, song_details in list(downloading_songs.items()):
        try:
            title = song_details.get('title', 'N/A')

            # Validate video ID
            if not validate_video_id(video_id):
                logger.error(f"Invalid video ID in downloads tracking: {video_id}")
                del st.session_state['download_requests'][video_id]
                continue

            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                with col1:
                    try:
                        st.image(song_details.get('thumbnail'), use_column_width=True)
                    except Exception as e:
                        logger.warning(f"Error displaying thumbnail for {video_id}: {e}")
                        st.write("🎵")  # Fallback icon

                with col2:
                    st.subheader(title)

                    try:
                        status_data: Dict[str, Any] = get_song_status(video_id)
                    except Exception as e:
                        logger.error(f"Error getting status for {video_id}: {e}")
                        st.error("שגיאה בקבלת סטטוס מהשרת")
                        continue

                    if not status_data or 'overall_status' not in status_data:
                        logger.warning(f"Waiting for status from server for song: '{title}' (video_id: {video_id})")
                        st.warning("ממתין לקבלת סטטוס מהשרת...")
                        continue

                    overall_status = status_data.get('overall_status', 'לא ידוע')
                    logger.info(f"Displaying status for '{title}': {overall_status}")

                    # Overall Progress
                    try:
                        progress = int(status_data.get('progress', 0))
                        progress = max(0, min(100, progress))  # Clamp between 0-100
                        st.progress(progress / 100, text=f"**סטטוס כללי:** {overall_status}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid progress value for {video_id}: {e}")
                        st.text(f"**סטטוס כללי:** {overall_status}")

                    # Detailed Stage Status
                    stages = {
                        "download": "הורדה מיוטיוב",
                        "audio_processing": "עיבוד אודיו (הפרדת ערוצים)",
                        "transcription": "תמלול ויצירת כתוביות"
                    }

                    stages_data = status_data.get('stages', {})
                    if isinstance(stages_data, dict):
                        for stage_key, stage_name in stages.items():
                            stage_status = stages_data.get(stage_key, "PENDING")
                            if stage_status == "COMPLETED":
                                st.markdown(f"- ✅ {stage_name}")
                            elif stage_status == "IN_PROGRESS":
                                st.markdown(f"- 🔄 {stage_name} (בתהליך...)")
                            elif stage_status == "FAILED":
                                st.markdown(f"- ❌ {stage_name} (נכשל)")
                            else:  # PENDING
                                st.markdown(f"- ⏳ {stage_name} (ממתין)")

                    # Handle completion or failure
                    if overall_status == "✅ מוכן לנגינה":
                        logger.info(f"Song '{title}' (video_id: {video_id}) is ready. Removing from tracking.")
                        st.success("השיר מוכן וזמין בספרייה!", icon="🎉")
                        # Remove from active downloads
                        del st.session_state['download_requests'][video_id]

                    elif overall_status == "❌ נכשל":
                        logger.error(f"Processing failed for song '{title}' (video_id: {video_id}). Removing from tracking.")
                        st.error("תהליך העיבוד נכשל. נסה להוריד שיר אחר.", icon="🔥")
                        # Remove from active downloads
                        del st.session_state['download_requests'][video_id]

        except Exception as e:
            logger.error(f"Error processing download status for {video_id}: {e}")
            try:
                # Try to remove problematic entry
                del st.session_state['download_requests'][video_id]
                logger.info(f"Removed problematic download entry: {video_id}")
            except KeyError:
                pass

    # Manual refresh logic
    if st.session_state.get('download_requests', {}):
        refresh_placeholder = st.empty()
        if refresh_placeholder.button("רענן סטטוסי הורדה"):
            logger.info("User manually refreshed download statuses.")
            st.rerun()
