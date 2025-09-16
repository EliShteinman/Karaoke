import streamlit as st
from services.streamlitClient.api.api_client import get_songs_library
from services.streamlitClient.api.helpers import seconds_to_mmss
from shared.utils import Logger

logger = Logger.get_logger()

st.set_page_config(page_title="ספריית השירים", page_icon="📚")
st.title("📚 ספריית השירים המוכנים")

# Initialize session state
if 'library' not in st.session_state:
    st.session_state['library'] = []

logger.info("Library page loaded.")

if st.button("🔄 רענן את הספרייה"):
    logger.info("User clicked 'Refresh Library' button.")
    with st.spinner("טוען את ספריית השירים..."):
        st.session_state['library'] = get_songs_library()
    logger.info(f"Library refreshed. Found {len(st.session_state['library'])} songs.")


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
        col = cols[i % 2]
        with col:
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(song.get('thumbnail'), use_column_width=True)
                with col2:
                    st.subheader(song.get('title', 'ללא כותרת'))
                    st.caption(f"אמן: {song.get('artist', 'לא ידוע')} | משך: {seconds_to_mmss(song.get('duration'))}")
                    st.caption(f"הורד בתאריך: {song.get('created_date', 'לא ידוע')}")
                
                if st.button("▶️ הפעל קריוקי", key=f"play_{song.get('video_id')}", use_container_width=True, type="primary"):
                    logger.info(f"User clicked 'Play Karaoke' for song: '{song.get('title', 'N/A')}' (video_id: {song.get('video_id')})")
                    # Set the song to be played and switch to the player page
                    st.session_state['song_to_play'] = song
                    st.switch_page("pages/4_🎤_נגן_קריוקי.py")
