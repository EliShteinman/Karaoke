import streamlit as st
from services.streamlitClient.config import StreamlitConfig

API_BASE_URL = StreamlitConfig.api_base_url
from shared.utils import Logger
logger = Logger.get_logger(
    name=StreamlitConfig.title,
    es_url=StreamlitConfig.es_url_logs,
    index=StreamlitConfig.es_index_logs,
    level=StreamlitConfig.log_es_level
)
st.set_page_config(page_title="🎤 Karaoke App", layout="wide", page_icon="🎶")
st.title("🎤 ברוך הבא לאפליקציית הקריוקי!")
st.write("בחר דף מתפריט הצד 👈 כדי להתחיל.")