import streamlit as st
from utils.api_client import search


st.title("🔍 חיפוש שירים")
query = st.text_input("הכנס שם שיר או אמן")
if st.button("חפש"):
    results = search(query)
    if results:
        st.session_state['results'] = results
        st.success(f"נמצאו {len(results)} תוצאות")
    else:
        st.info("לא נמצאו תוצאות")

