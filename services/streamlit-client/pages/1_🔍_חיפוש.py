import streamlit as st
from utils.api_client import search, download_song
from utils.helpers import show_youtube_player

st.set_page_config(page_title="חיפוש שירים", page_icon="🔍")
st.title("🔍 חיפוש והורדת שירים")

# Initialize session state variables
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = []
if 'download_requests' not in st.session_state:
    st.session_state['download_requests'] = {}

# --- Search Form ---
with st.form(key="search_form"):
    query = st.text_input("הקלד שם שיר, אמן, או מילות מפתח", placeholder="לדוגמה: Queen Bohemian Rhapsody")
    submit_button = st.form_submit_button(label="חפש ביוטיוב")

if submit_button and query:
    with st.spinner("מחפש, אנא המתן..."):
        results = search(query)
        st.session_state['search_results'] = results
        if not results:
            st.info("לא נמצאו תוצאות עבור החיפוש שלך.")

# --- Results Display ---
if st.session_state['search_results']:
    st.markdown("--- ")
    st.subheader("תוצאות החיפוש")

    # Display in a 3-column grid
    cols = st.columns(3)
    for i, song in enumerate(st.session_state['search_results']):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.image(song.get('thumbnail'), use_column_width=True)
                st.markdown(f"**{song['title']}**")
                st.caption(f"ערוץ: {song['channel']} | משך: {int(song['duration'] // 60)}:{(song['duration'] % 60):02d}")

                # Download button
                video_id = song['video_id']
                if video_id in st.session_state.get('download_requests', {}):
                    st.button("הורדה התחילה ✅", key=f"download_{video_id}", disabled=True)
                else:
                    if st.button("הורד שיר זה ⬇️", key=f"download_{video_id}"):
                        with st.spinner("שולח בקשת הורדה..."):
                            response = download_song(song)
                            if response and response.get('status') == 'queued':
                                st.success(f"השיר '{song['title']}' נוסף לתור ההורדות!")
                                # Add to session state for tracking on the downloads page
                                st.session_state['download_requests'][video_id] = song
                                st.rerun()
                            else:
                                st.error("ההורדה נכשלה. נסה שוב או בחר שיר אחר.")

            # Optional: Show a preview player
            with st.expander("צפה בתצוגה מקדימה"):
                show_youtube_player(song['video_id'])
