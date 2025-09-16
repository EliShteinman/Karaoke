import streamlit as st
from services.streamlitClient.api.api_client import get_songs_library
from services.streamlitClient.api.helpers import seconds_to_mmss

st.set_page_config(page_title="ספריית השירים", page_icon="📚")
st.title("📚 ספריית השירים המוכנים")

# Initialize session state
if 'library' not in st.session_state:
    st.session_state['library'] = []

if st.button("🔄 רענן את הספרייה"):
    with st.spinner("טוען את ספריית השירים..."):
        st.session_state['library'] = get_songs_library()

if not st.session_state['library']:
    st.info("ספריית השירים ריקה. הורד שירים חדשים כדי להתחיל.")
    if st.button("חפש שירים להורדה"):
        st.switch_page("pages/1_🔍_חיפוש.py")
else:
    st.markdown("בחר שיר כדי להתחיל לשיר!")
    
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
                    # Set the song to be played and switch to the player page
                    st.session_state['song_to_play'] = song
                    st.switch_page("pages/4_🎤_נגן_קריוקי.py")
