"""
Text processing utilities for transcription service
"""
import re

from unidecode import unidecode


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = unidecode(text)  # remove special characters
    return text
