import os
import logging
from typing import Optional

from shared.utils.logger import Logger


class StreamlitConfig:
    """
    Configuration for Streamlit client
    Uses: HTTP connection to API Server
    """
    # API connection - REQUIRED by shared/http tools
    api_base_url: str = os.getenv("API_SERVER_URL", "http://localhost:8000")

    # Logging configuration
    title: str = os.getenv("STREAMLIT_TITLE", "streamlitClient")
    es_url_logs: str = os.getenv("LOG_ELASTICSEARCH_URL", "http://localhost:9200")
    es_index_logs: str = os.getenv("LOG_ELASTICSEARCH_INDEX", "logs")
    log_es_level: str = os.getenv("STREAMLIT_LOG_ES_LEVEL", "DEBUG")

    # UI Configuration
    app_title: str = os.getenv("STREAMLIT_APP_TITLE", "🎤 Karaoke System")
    app_icon: str = os.getenv("STREAMLIT_APP_ICON", "🎶")
    page_layout: str = os.getenv("STREAMLIT_PAGE_LAYOUT", "wide")

    # Performance settings
    request_timeout: int = int(os.getenv("STREAMLIT_REQUEST_TIMEOUT", "30"))
    cache_ttl: int = int(os.getenv("STREAMLIT_CACHE_TTL", "300"))
    polling_interval: int = int(os.getenv("STREAMLIT_POLLING_INTERVAL", "5"))

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """Get configured logger instance using shared logger"""
        logger_name = name or cls.title
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = level_map.get(cls.log_es_level, logging.DEBUG)

        return Logger.get_logger(
            name=logger_name,
            es_url=cls.es_url_logs,
            index=cls.es_index_logs,
            level=log_level
        )
