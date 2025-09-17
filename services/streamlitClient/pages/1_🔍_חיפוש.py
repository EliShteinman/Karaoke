import streamlit as st
from services.streamlitClient.config import StreamlitConfig
from services.streamlitClient.api.api_client import search, download_song
from services.streamlitClient.api.helpers import show_youtube_player, validate_video_id

logger = StreamlitConfig.get_logger(__name__)
st.set_page_config(page_title="חיפוש שירים", page_icon="🔍")
st.title("🔍 חיפוש והורדת שירים")

logger.info("Search page loaded")
logger.debug("Search page: Initializing search page components")

# Initialize session state variables
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = []
if 'last_search_query' not in st.session_state:
    st.session_state['last_search_query'] = ''
if 'downloading_songs' not in st.session_state:
    st.session_state.downloading_songs = {}

# --- Search Form ---
with st.form(key="search_form"):
    query = st.text_input("הקלד שם שיר, אמן, או מילות מפתח", placeholder="לדוגמה: Queen Bohemian Rhapsody")
    submit_button = st.form_submit_button(label="חפש ביוטיוב")

if submit_button and query:
    logger.info(f"User searched for: '{query}'")
    with st.spinner("מחפש, אנא המתן..."):
        results = search(query)
        logger.debug(f"Search results: {results}")
        st.session_state['search_results'] = results
        st.session_state['last_search_query'] = query
        if not results:
            logger.info(f"No search results found for query: '{query}'")
            st.info("לא נמצאו תוצאות עבור החיפוש שלך.")
        else:
            st.success(f"נמצאו {len(results)} תוצאות עבור '{query}'")

# --- Results Display ---
if st.session_state['search_results']:
    logger.debug(f"Search page: Displaying {len(st.session_state['search_results'])} search results")
    st.markdown("--- ")
    st.subheader("תוצאות החיפוש")

    # Display in a 3-column grid
    cols = st.columns(3)
    for i, song in enumerate(st.session_state['search_results']):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.image(song.get('thumbnail'), width='stretch')
                st.markdown(f"**{song['title']}**")
                st.caption(f"ערוץ: {song['channel']} | משך: {int(song['duration'] // 60)}:{(song['duration'] % 60):02d}")

                # Download button
                video_id = song['video_id']
                if not validate_video_id(video_id):
                    logger.error(f"Invalid video ID format: {video_id}")
                    st.error("מזהה הוידאו אינו תקין")
                elif False:  # Remove local tracking - let API handle this
                    st.button("הורדה התחילה ✅", key=f"download_{video_id}", disabled=True)
                else:
                    if st.button("הורד שיר זה ⬇️", key=f"download_{video_id}"):
                        logger.info(f"User initiated download for song: '{song['title']}' (video_id: {video_id})")
                        try:
                            with st.spinner("שולח בקשת הורדה..."):
                                response = download_song(song)
                                if response and response.get('status') == 'accepted':
                                    logger.info(f"Successfully queued download for song: '{song['title']}'")
                                    st.success(f"✅ השיר '{song['title']}' נוסף לתור ההורדות!")
                                    st.info("💡 ניתן לעקוב אחר התקדמות העיבוד בדף 'הורדות'")
                                    # Add song to downloading_songs for tracking
                                    st.session_state.downloading_songs[video_id] = song
                                    logger.debug(f"Added song {video_id} to downloading_songs tracking")
                                    # Clear cache to reflect new download
                                    st.cache_data.clear()
                                    # Small delay to show success message
                                    import time
                                    time.sleep(1.5)
                                else:
                                    logger.error(f"Failed to queue download for song: '{song['title']}'. Response: {response}")
                                    st.error("❌ ההורדה נכשלה. נסה שוב או בחר שיר אחר.")
                        except Exception as e:
                            logger.error(f"Unexpected error during download request: {e}")
                            st.error("שגיאה לא צפויה בבקשת ההורדה")

            # Optional: Show a preview player
            try:
                with st.expander("צפה בתצוגה מקדימה"):
                    show_youtube_player(song['video_id'])
            except Exception as e:
                logger.error(f"Error showing YouTube player for {video_id}: {e}")
