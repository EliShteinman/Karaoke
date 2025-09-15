"""
ממשק משתמש Streamlit עברי לקריוקי
"""

import streamlit as st
from typing import Dict, Any
import time

# הגדרת תצורת עמוד עברי
st.set_page_config(
    page_title="HebKaraoke - קריוקי עברי",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS עברי RTL
st.markdown("""
<style>
    .main > div {
        direction: rtl;
        text-align: right;
    }
    .stTextInput > div > div > input {
        direction: ltr;
    }
</style>
""", unsafe_allow_html=True)


class KaraokeUI:
    """
    ממשק קריוקי עברי
    """

    def __init__(self):
        # TODO: מפתח E - כתוב את הלוגיקה כאן
        pass

    def render_home_page(self):
        """
        עמוד בית
        """
        st.title("🎤 HebKaraoke - קריוקי עברי")
        st.write("ברוכים הבאים למערכת הקריוקי העברית!")
        # TODO: מפתח E - כתוב את הלוגיקה כאן

    def render_upload_page(self):
        """
        עמוד העלאה
        """
        st.header("📤 העלאת שיר חדש")
        youtube_url = st.text_input("קישור יוטיוב:")
        if st.button("הורד ועבד"):
            # TODO: מפתח E - כתוב את הלוגיקה כאן
            pass

    def render_karaoke_page(self):
        """
        עמוד קריוקי
        """
        st.header("🎵 נגן קריוקי")
        # TODO: מפתח E - כתוב את הלוגיקה כאן
        pass

    def render_status_page(self):
        """
        עמוד סטטוס עבודות
        """
        st.header("📊 סטטוס עיבוד")
        # TODO: מפתח E - כתוב את הלוגיקה כאן
        pass


def main():
    """
    פונקציה ראשית
    """
    ui = KaraokeUI()

    # תפריט צד
    page = st.sidebar.selectbox(
        "בחר עמוד:",
        ["בית", "העלאה", "קריוקי", "סטטוס"]
    )

    if page == "בית":
        ui.render_home_page()
    elif page == "העלאה":
        ui.render_upload_page()
    elif page == "קריוקי":
        ui.render_karaoke_page()
    elif page == "סטטוס":
        ui.render_status_page()


if __name__ == "__main__":
    main()