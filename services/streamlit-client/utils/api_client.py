import requests
import streamlit as st
from config import API_BASE_URL

def search(query: str):
    """Sends a search request to the API server."""
    try:
        response = requests.post(f"{API_BASE_URL}/search", json={"query": query}, timeout=15)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException as e:
        st.error(f"שגיאת רשת בחיפוש: {e}")
        return []

def download_song(song_details: dict):
    """Sends a download request for a specific song."""
    try:
        response = requests.post(f"{API_BASE_URL}/download", json=song_details, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"שגיאת רשת בעת בקשת הורדה: {e}")
        return None

def get_songs_library():
    """Fetches the list of ready songs from the library."""
    try:
        response = requests.get(f"{API_BASE_URL}/songs", timeout=15)
        response.raise_for_status()
        return response.json().get("songs", [])
    except requests.RequestException as e:
        st.error(f"שגיאת רשת בטעינת הספרייה: {e}")
        return []

def get_song_status(video_id: str):
    """Fetches the processing status of a song."""
    try:
        response = requests.get(f"{API_BASE_URL}/songs/{video_id}/status", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        # Don't show error for status checks, as it can be noisy during polling
        return {}

def get_song_assets(video_id: str):
    """Downloads the karaoke assets (audio and LRC file) for a given song."""
    try:
        response = requests.get(f"{API_BASE_URL}/songs/{video_id}/download", timeout=60)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        st.error(f"שגיאה בהורדת קבצי הקריוקי: {e}")
        return None
