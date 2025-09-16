import os

import requests
import streamlit as st
API_BASE = os.getenv("api_base", "http://localhost:8000")


def search(query: str):
    try:
        r = requests.post(f"{API_BASE}/search", json={"query": query}, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        st.error(f"שגיאה בבקשת החיפוש: {e}")
        return []


def download(song: dict):
    try:
        r = requests.post(f"{API_BASE}/download", json=song, timeout=10)
        r.raise_for_status()
        st.success("✅ בקשת ההורדה נשלחה")
    except Exception as e:
        st.error(f"שגיאה בהורדה: {e}")


def get_songs():
    try:
        r = requests.get(f"{API_BASE}/songs", timeout=10)
        r.raise_for_status()
        return r.json().get("songs", [])
    except Exception as e:
        st.error(f"שגיאה בטעינת ספרייה: {e}")
        return []




def get_status(video_id: str):
    try:
        r = requests.get(f"{API_BASE}/songs/{video_id}/status", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"שגיאה בסטטוס: {e}")
        return {}



