import streamlit as st
from utils.lrc_parser import parse_lrc
import os


st.title("▶️ נגן קריוקי")
TMP_DIR = "./tmp_karaoke"
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
local_dirs = [d for d in os.listdir(TMP_DIR) if os.path.isdir(os.path.join(TMP_DIR,d))]
video_id = st.selectbox("בחר שיר מקומי", local_dirs)
if video_id:
    base = os.path.join(TMP_DIR, video_id)
    audio_file = None
    lrc_file = None
    for f in os.listdir(base):
        if f.endswith('.mp3'):
            audio_file = os.path.join(base,f)
        if f.endswith('.lrc'):
            lrc_file = os.path.join(base,f)


    if audio_file:
        st.audio(audio_file)
    if lrc_file:
        with open(lrc_file,'r',encoding='utf-8') as fh:
            lrc_text = fh.read()
        lines = parse_lrc(lrc_text)
        for ln in lines[:10]: # הצגת דוגמא ראשונה בלבד
            st.write(f"{ln.timestamp:.2f} - {ln.text}")
else:
    st.write("לא נמצאו שירים מקומיים")
