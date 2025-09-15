"""
Kafka Consumer משותף לכל השירותים
"""

from typing import Callable, Dict, Any
from kafka import KafkaConsumer
import threading


class HebKaraokeConsumer:
    """
    Kafka consumer משותף עם תצורה אחידה
    """

    def __init__(self, topics: list, group_id: str, bootstrap_servers: str = "localhost:9092"):
        """
        אתחול Kafka consumer

        Args:
            topics: רשימת topics להאזנה
            group_id: מזהה קבוצת צרכנים
            bootstrap_servers: כתובת שרתי Kafka
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass

    def start_listening(self, message_handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        התחלת האזנה להודעות

        Args:
            message_handler: פונקציה לטיפול בהודעות
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass

    def stop_listening(self) -> None:
        """
        הפסקת האזנה
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass

    def _consume_messages(self, message_handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        לולאת צריכת הודעות (פנימית)

        Args:
            message_handler: פונקציה לטיפול בהודעות
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass