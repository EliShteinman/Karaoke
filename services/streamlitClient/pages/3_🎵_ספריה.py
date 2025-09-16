import streamlit as st
from typing import List, Dict, Any
from services.streamlitClient.api.api_client import get_songs_library
from services.streamlitClient.api.helpers import seconds_to_mmss, validate_video_id
from services.streamlitClient.config import StreamlitConfig

logger = StreamlitConfig.get_logger(__name__)

st.set_page_config(page_title="ספריית השירים", page_icon="📚")
st.title("📚 ספריית השירים המוכנים")

# Initialize session state
if 'library' not in st.session_state:
    st.session_state['library'] = []

logger.info("Library page loaded.")

if st.button("🔄 רענן את הספרייה"):
    logger.info("User clicked 'Refresh Library' button.")
    try:
        with st.spinner("טוען את ספריית השירים..."):
            library_songs: List[Dict[str, Any]] = get_songs_library()
            st.session_state['library'] = library_songs
        logger.info(f"Library refreshed. Found {len(st.session_state['library'])} songs.")
        st.success(f"הספרייה נטענה בהצלחה - נמצאו {len(st.session_state['library'])} שירים")
    except Exception as e:
        logger.error(f"Error refreshing library: {e}")
        st.error("שגיאה בטעינת הספרייה")


if not st.session_state['library']:
    logger.info("Song library is empty.")
    st.info("ספריית השירים ריקה. הורד שירים חדשים כדי להתחיל.")
    if st.button("חפש שירים להורדה"):
        logger.info("User clicked 'Search for songs' from empty library page.")
        st.switch_page("pages/1_🔍_חיפוש.py")
else:
    st.markdown("בחר שיר כדי להתחיל לשיר!")
    logger.info(f"Displaying {len(st.session_state['library'])} songs in the library.")

    # Display songs in a 2-column grid
    cols = st.columns(2)
    for i, song in enumerate(st.session_state['library']):
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
                            st.image(song.get('thumbnail'), use_column_width=True)
                        except Exception as e:
                            logger.warning(f"Error displaying thumbnail for {video_id}: {e}")
                            st.write("🎵")  # Fallback icon

                    with col2:
                        st.subheader(song.get('title', 'ללא כותרת'))
                        try:
                            duration_str = seconds_to_mmss(song.get('duration'))
                            st.caption(f"אמן: {song.get('artist', 'לא ידוע')} | משך: {duration_str}")
                        except Exception as e:
                            logger.warning(f"Error formatting duration for {video_id}: {e}")
                            st.caption(f"אמן: {song.get('artist', 'לא ידוע')}")

                        st.caption(f"הורד בתאריך: {song.get('created_date', 'לא ידוע')}")

                    if st.button("▶️ הפעל קריוקי", key=f"play_{video_id}", use_container_width=True, type="primary"):
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
