import streamlit as st
from utils.api_client import download


st.title("⬇️ הורדות")
results = st.session_state.get('results', [])
if not results:
    st.info("בצע חיפוש בעמוד 'חיפוש' כדי לראות תוצאות")
else:
    for song in results:
        st.image(song.get('thumbnail'), width=150)
        st.write(f"**{song['title']}** - {song['channel']}")
        if st.button(f"הורד {song['video_id']}", key=song['video_id']):
            download(song)