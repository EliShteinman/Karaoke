"""
Kafka Producer משותף לכל השירותים
"""

from typing import Dict, Any
from kafka import KafkaProducer
import json


class HebKaraokeProducer:
    """
    Kafka producer משותף עם תצורה אחידה
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        אתחול Kafka producer

        Args:
            bootstrap_servers: כתובת שרתי Kafka
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass

    def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        """
        שליחת הודעה ל-topic

        Args:
            topic: נושא Kafka
            message: תוכן ההודעה
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass

    def send_job_request(self, from_service: str, to_service: str, job_id: str, song_id: str, payload: Dict[str, Any]) -> None:
        """
        שליחת בקשת עבודה בין שירותים

        Args:
            from_service: שירות שולח
            to_service: שירות מקבל
            job_id: מזהה עבודה
            song_id: מזהה שיר
            payload: נתונים נוספים
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass

    def close(self) -> None:
        """
        סגירת החיבור
        """
        # TODO: מפתח - כתוב את הלוגיקה כאן
        pass