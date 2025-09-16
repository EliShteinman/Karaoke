import streamlit as st
from utils.api_client import get_songs


st.title("📚 ספרייה")
if st.button("טען ספרייה מהשרת"):
    st.session_state['library'] = get_songs()


library = st.session_state.get('library', [])
for s in library:
    st.image(s.get('thumbnail'), width=150)
    st.write(f"**{s['title']}** - {s['channel']} ({s.get('duration','?')}s)")
    if st.button(f"נגן {s['video_id']}", key=f"play_{s['video_id']}"):
        st.write(f"הפעלת השיר: {s['title']}")