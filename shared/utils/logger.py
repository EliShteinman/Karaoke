import logging
import os
from datetime import datetime, timezone

from elasticsearch import Elasticsearch


class LogConfig:
    """
    Configuration settings for the logger, loaded from environment variables.
    Provides default values for local development if variables are not set.
    """
    LOG_ELASTICSEARCH_SCHEME = os.getenv("LOG_ELASTICSEARCH_SCHEME", "http")
    LOG_ELASTICSEARCH_HOST = os.getenv("LOG_ELASTICSEARCH_HOST", "localhost")
    LOG_ELASTICSEARCH_PORT = int(os.getenv("LOG_ELASTICSEARCH_PORT", 9200))
    LOG_ELASTICSEARCH_INDEX_LOG = os.getenv("LOG_ELASTICSEARCH_INDEX_LOG", "logs")


class Logger:
    """
    A singleton logger provider that creates and manages a single logger instance.

    This class ensures that the entire application uses the same logger, which is
    configured to send logs to two destinations:
    1. The console (standard output) for real-time monitoring.
    2. An Elasticsearch index for centralized log storage and analysis.
    """
    _logger = None

    @classmethod
    def get_logger(
        cls,
        name=__name__,
        es_url=f"{LogConfig.LOG_ELASTICSEARCH_SCHEME}://{LogConfig.LOG_ELASTICSEARCH_HOST}:{LogConfig.LOG_ELASTICSEARCH_PORT}",
        index=LogConfig.LOG_ELASTICSEARCH_INDEX_LOG,
        level=logging.DEBUG,
    ):
        """
        Retrieves the singleton logger instance, creating it if it doesn't exist.

        On the first call, it initializes a new logger, sets its level, and
        configures handlers for Elasticsearch and the console. Subsequent calls
        will return the already created instance.

        Args:
            name (str): The name of the logger. Defaults to the module name.
            es_url (str): The full URL for the Elasticsearch instance.
                          Defaults to the URL constructed from LogConfig.
            index (str): The Elasticsearch index where logs will be stored.
                         Defaults to the index from LogConfig.
            level (int): The minimum logging level to process.
                         Defaults to logging.DEBUG.

        Returns:
            logging.Logger: The configured singleton logger instance.
        """
        if cls._logger:
            return cls._logger

        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Add handlers only if they haven't been added before.
        if not logger.handlers:
            # 1. Configure and add the Elasticsearch handler.
            try:
                es_client = Elasticsearch(es_url)

                class ESHandler(logging.Handler):
                    """
                    A custom logging handler to send log records to Elasticsearch.
                    """
                    def emit(self, record):
                        """
                        Formats the log record and sends it to Elasticsearch.
                        If the operation fails, an error is printed to the console.
                        """
                        try:
                            log_document = {
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "level": record.levelname,
                                "logger": record.name,
                                "message": record.getMessage(),
                            }
                            es_client.index(index=index, document=log_document)
                        except Exception as e:
                            print(f"Error: Could not send log to Elasticsearch. {e}")

                logger.addHandler(ESHandler())
            except Exception as e:
                print(f"Error: Could not connect to Elasticsearch at {es_url}. {e}")

            # 2. Configure and add the console stream handler.
            logger.addHandler(logging.StreamHandler())

        cls._logger = logger
        return logger