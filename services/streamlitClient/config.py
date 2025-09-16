import os

class StreamlitConfig:

    """
    Configuration for Streamlit client
    Uses: HTTP connection to API Server
    """
    # API connection - REQUIRED by shared/http tools
    api_base_url= os.getenv("STREAMLIT_API_BASE_URL", "http://localhost:8000")
    # log
    title = os.getenv("STREAMLIT_TITLE", "streamlitClient")
    es_url_logs = os.getenv("STREAMLIT_ES_URL_LOGS", "http://localhost:9200")
    es_index_logs = os.getenv("STREAMLIT_ES_INDEX_LOGS", "logs")
    log_es_level = os.getenv("STREAMLIT_LOG_ES_LEVEL", "DEBUG")
