import requests
import streamlit as st
from services.streamlitClient.app import API_BASE_URL
from shared.utils import Logger

logger = Logger.get_logger()


def search(query: str):
    """Sends a search request to the API server."""
    logger.info(f"Searching for: '{query}'")
    try:
        response = requests.post(f"{API_BASE_URL}/search", json={"query": query}, timeout=15)
        response.raise_for_status()
        results = response.json().get("results", [])
        logger.info(f"Found {len(results)} results for '{query}'")
        return results
    except requests.RequestException as e:
        logger.error(f"Network error during search for '{query}': {e}")
        st.error(f"שגיאת רשת בחיפוש: {e}")
        return []


def download_song(song_details: dict):
    """Sends a download request for a specific song."""
    video_id = song_details.get('video_id', 'N/A')
    title = song_details.get('title', 'N/A')
    logger.info(f"Requesting download for song: '{title}' (video_id: {video_id})")
    try:
        response = requests.post(f"{API_BASE_URL}/download", json=song_details, timeout=15)
        response.raise_for_status()
        logger.info(f"Successfully queued download for '{title}'")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Network error during download request for '{title}': {e}")
        st.error(f"שגיאת רשת בעת בקשת הורדה: {e}")
        return None


def get_songs_library():
    """Fetches the list of ready songs from the library."""
    logger.info("Fetching songs library...")
    try:
        response = requests.get(f"{API_BASE_URL}/songs", timeout=15)
        response.raise_for_status()
        songs = response.json().get("songs", [])
        logger.info(f"Successfully fetched {len(songs)} songs from the library.")
        return songs
    except requests.RequestException as e:
        logger.error(f"Network error while fetching song library: {e}")
        st.error(f"שגיאת רשת בטעינת הספרייה: {e}")
        return []


def get_song_status(video_id: str):
    """Fetches the processing status of a song."""
    logger.debug(f"Fetching status for video_id: {video_id}")
    try:
        response = requests.get(f"{API_BASE_URL}/songs/{video_id}/status", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Don't show UI error for status checks, as it can be noisy, but log it.
        logger.warning(f"Network error while fetching status for video_id '{video_id}': {e}")
        return {}


def get_song_assets(video_id: str):
    """Downloads the karaoke assets (audio and LRC file) for a given song."""
    logger.info(f"Downloading assets for video_id: {video_id}")
    try:
        response = requests.get(f"{API_BASE_URL}/songs/{video_id}/download", timeout=60)
        response.raise_for_status()
        logger.info(f"Successfully downloaded assets for video_id: {video_id}")
        return response.content
    except requests.RequestException as e:
        logger.error(f"Failed to download assets for video_id '{video_id}': {e}")
        st.error(f"שגיאה בהורדת קבצי הקריוקי: {e}")
        return None
