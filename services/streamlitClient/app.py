import streamlit as st
from services.streamlitClient.config import StreamlitConfig

# Configure logger using shared utilities
logger = StreamlitConfig.get_logger(__name__)

# Set page configuration
st.set_page_config(
    page_title=StreamlitConfig.app_title,
    layout=StreamlitConfig.page_layout,
    page_icon=StreamlitConfig.app_icon
)

logger.info("Streamlit application started - main page loaded")

# Main page content
st.title("🎤 ברוך הבא לאפליקציית הקריוקי!")
st.write("בחר דף מתפריט הצד 👈 כדי להתחיל.")

logger.info("Main page rendered successfully")