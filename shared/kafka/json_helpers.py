import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def serialize_json(data: Any) -> str:
    """
    Convert Python object to JSON string
    With support for datetime and complex objects

    Args:
        data: Data to convert

    Returns:
        JSON string

    Raises:
        ValueError: If conversion fails
    """

    def json_serializer(obj):
        """Custom serializer"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return str(obj)

    try:
        return json.dumps(
            data, default=json_serializer, ensure_ascii=False, indent=None
        )
    except Exception as e:
        logger.error(f"Failed to serialize JSON: {e}")
        raise ValueError(f"JSON serialization failed: {e}")


def deserialize_json(json_str: str) -> Any:
    """
    Convert JSON string to Python object
    With error handling

    Args:
        json_str: JSON string

    Returns:
        Python object

    Raises:
        ValueError: If conversion fails
    """
    if not json_str or not isinstance(json_str, str):
        raise ValueError("Invalid JSON string provided")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to deserialize JSON: {e}")
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in JSON deserialization: {e}")
        raise ValueError(f"JSON deserialization failed: {e}")


def create_kafka_message(
    topic: str, data: Any, key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standard Kafka message with metadata

    Args:
        topic: Topic name
        data: The data itself
        key: Optional key

    Returns:
        Dictionary with standard Kafka message structure
    """
    timestamp = datetime.now()

    return {
        "topic": topic,
        "key": key,
        "data": data,
        "timestamp": timestamp.isoformat(),
        "message_id": f"{topic}_{timestamp.timestamp()}",
        "created_at": timestamp.isoformat(),
        "version": "1.0",
    }
