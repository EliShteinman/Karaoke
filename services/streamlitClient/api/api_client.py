import requests
import streamlit as st
from typing import List, Optional, Dict, Any
from pydantic import ValidationError

from services.streamlitClient.config import StreamlitConfig
from services.streamlitClient.models import (
    SearchRequest, SearchResponse, DownloadRequest, DownloadResponse,
    SongStatus, LibraryResponse, LibrarySong
)

# Configure logger and get API base URL
logger = StreamlitConfig.get_logger(__name__)
API_BASE_URL = StreamlitConfig.api_base_url


def search(query: str) -> List[Dict[str, Any]]:
    """
    Sends a search request to the API server.

    Args:
        query: Search query string

    Returns:
        List of search results as dictionaries
    """
    logger.info(f"Searching for: '{query}'")

    try:
        # Validate input using Pydantic model
        search_request = SearchRequest(query=query)

        response = requests.post(
            f"{API_BASE_URL}/search",
            json=search_request.dict(),
            timeout=StreamlitConfig.request_timeout
        )
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        search_response = SearchResponse(**response_data)

        results = [result.dict() for result in search_response.results]
        logger.info(f"Found {len(results)} results for '{query}'")
        return results

    except ValidationError as e:
        logger.error(f"Validation error during search for '{query}': {e}")
        st.error(f"שגיאה בוולידציה של בקשת החיפוש: {e}")
        return []
    except requests.RequestException as e:
        logger.error(f"Network error during search for '{query}': {e}")
        st.error(f"שגיאת רשת בחיפוש: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during search for '{query}': {e}")
        st.error(f"שגיאה לא צפויה בחיפוש: {e}")
        return []


def download_song(song_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sends a download request for a specific song.

    Args:
        song_details: Dictionary containing song information

    Returns:
        Download response dictionary or None if failed
    """
    video_id = song_details.get('video_id', 'N/A')
    title = song_details.get('title', 'N/A')
    logger.info(f"Requesting download for song: '{title}' (video_id: {video_id})")

    try:
        # Validate input using Pydantic model
        download_request = DownloadRequest(**song_details)

        response = requests.post(
            f"{API_BASE_URL}/download",
            json=download_request.dict(),
            timeout=StreamlitConfig.request_timeout
        )
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        download_response = DownloadResponse(**response_data)

        logger.info(f"Successfully queued download for '{title}'")
        return download_response.dict()

    except ValidationError as e:
        logger.error(f"Validation error during download request for '{title}': {e}")
        st.error(f"שגיאה בוולידציה של בקשת ההורדה: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Network error during download request for '{title}': {e}")
        st.error(f"שגיאת רשת בעת בקשת הורדה: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during download request for '{title}': {e}")
        st.error(f"שגיאה לא צפויה בבקשת הורדה: {e}")
        return None


def get_songs_library() -> List[Dict[str, Any]]:
    """
    Fetches the list of ready songs from the library.

    Returns:
        List of library songs as dictionaries
    """
    logger.info("Fetching songs library...")

    try:
        response = requests.get(
            f"{API_BASE_URL}/songs",
            timeout=StreamlitConfig.request_timeout
        )
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        library_response = LibraryResponse(**response_data)

        songs = [song.dict() for song in library_response.songs]
        logger.info(f"Successfully fetched {len(songs)} songs from the library.")
        return songs

    except ValidationError as e:
        logger.error(f"Validation error while fetching song library: {e}")
        st.error(f"שגיאה בוולידציה של נתוני הספרייה: {e}")
        return []
    except requests.RequestException as e:
        logger.error(f"Network error while fetching song library: {e}")
        st.error(f"שגיאת רשת בטעינת הספרייה: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching song library: {e}")
        st.error(f"שגיאה לא צפויה בטעינת הספרייה: {e}")
        return []


def get_song_status(video_id: str) -> Dict[str, Any]:
    """
    Fetches the processing status of a song.

    Args:
        video_id: YouTube video ID

    Returns:
        Song status dictionary
    """
    logger.debug(f"Fetching status for video_id: {video_id}")

    try:
        response = requests.get(
            f"{API_BASE_URL}/songs/{video_id}/status",
            timeout=StreamlitConfig.request_timeout
        )
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        song_status = SongStatus(**response_data)

        return song_status.dict()

    except ValidationError as e:
        logger.warning(f"Validation error while fetching status for video_id '{video_id}': {e}")
        return {}
    except requests.RequestException as e:
        # Don't show UI error for status checks, as it can be noisy, but log it.
        logger.warning(f"Network error while fetching status for video_id '{video_id}': {e}")
        return {}
    except Exception as e:
        logger.warning(f"Unexpected error while fetching status for video_id '{video_id}': {e}")
        return {}


def get_song_assets(video_id: str) -> Optional[bytes]:
    """
    Downloads the karaoke assets (audio and LRC file) for a given song.

    Args:
        video_id: YouTube video ID

    Returns:
        Binary content of the ZIP file or None if failed
    """
    logger.info(f"Downloading assets for video_id: {video_id}")

    try:
        response = requests.get(
            f"{API_BASE_URL}/songs/{video_id}/download",
            timeout=60  # Longer timeout for file download
        )
        response.raise_for_status()

        logger.info(f"Successfully downloaded assets for video_id: {video_id} ({len(response.content)} bytes)")
        return response.content

    except requests.RequestException as e:
        logger.error(f"Failed to download assets for video_id '{video_id}': {e}")
        st.error(f"שגיאה בהורדת קבצי הקריוקי: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading assets for video_id '{video_id}': {e}")
        st.error(f"שגיאה לא צפויה בהורדת קבצי הקריוקי: {e}")
        return None
