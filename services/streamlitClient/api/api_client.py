import requests
import streamlit as st
import json
from typing import List, Optional, Dict, Any
from pydantic import ValidationError

from services.streamlitClient.config import StreamlitConfig
from services.streamlitClient.models import (
    SearchRequest, SearchResponse, DownloadRequest, DownloadResponse,
    SongStatus, SongsResponse, SongListItem
)

# Configure logger and get API base URL
logger = StreamlitConfig.get_logger(__name__)
API_BASE_URL = StreamlitConfig.api_base_url

def log_request_response(method: str, url: str, request_data: Any = None, response: requests.Response = None, error: Exception = None):
    """Log detailed request and response information"""
    logger.info(f"🌐 HTTP {method.upper()} Request to: {url}")

    if request_data:
        logger.info(f"📤 Request Data: {json.dumps(request_data, ensure_ascii=False, indent=2)}")

    if response:
        logger.info(f"📥 Response Status: {response.status_code}")
        logger.info(f"📥 Response Headers: {dict(response.headers)}")
        try:
            response_json = response.json()
            logger.info(f"📥 Response Body: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        except:
            logger.info(f"📥 Response Body (raw): {response.text}")

    if error:
        logger.error(f"❌ Request Error: {type(error).__name__}: {error}")

    logger.debug(f"🔍 Full URL: {url}")
    logger.debug(f"🔍 API Base URL: {API_BASE_URL}")


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def search(query: str) -> List[Dict[str, Any]]:
    """
    Sends a search request to the API server.

    Args:
        query: Search query string

    Returns:
        List of search results as dictionaries
    """
    logger.info(f"API Client: Starting search for query: '{query}' (cache miss)")
    logger.debug(f"API Client: Search function called with query: '{query}'")

    url = f"{API_BASE_URL}/search"
    request_data = None
    response = None

    try:
        # Validate input using Pydantic model
        search_request = SearchRequest(query=query)
        request_data = search_request.model_dump(mode='json')

        log_request_response("POST", url, request_data)

        response = requests.post(
            url,
            json=request_data,
            timeout=StreamlitConfig.request_timeout
        )

        log_request_response("POST", url, request_data, response)
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        search_response = SearchResponse(**response_data)

        results = [result.model_dump() for result in search_response.results]
        logger.info(f"API Client: Successfully completed search for '{query}', found {len(results)} results")
        logger.debug(f"API Client: Search results: {[r.get('title', 'N/A') for r in results]}")
        return results

    except ValidationError as e:
        log_request_response("POST", url, request_data, response, e)
        logger.error(f"Validation error during search for '{query}': {e}")
        st.error(f"שגיאה בוולידציה של בקשת החיפוש: {e}")
        return []
    except requests.RequestException as e:
        log_request_response("POST", url, request_data, response, e)
        logger.error(f"Network error during search for '{query}': {e}")
        st.error(f"שגיאת רשת בחיפוש: {e}")
        return []
    except Exception as e:
        log_request_response("POST", url, request_data, response, e)
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
    logger.info(f"API Client: Starting download request for song: '{title}' (video_id: {video_id})")
    logger.debug(f"API Client: Download function called with song_details: {song_details}")

    url = f"{API_BASE_URL}/download"
    request_data = None
    response = None

    try:
        # Validate input using Pydantic model
        download_request = DownloadRequest(**song_details)
        request_data = download_request.model_dump(mode='json')

        log_request_response("POST", url, request_data)

        response = requests.post(
            url,
            json=request_data,
            timeout=StreamlitConfig.request_timeout
        )

        log_request_response("POST", url, request_data, response)
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        download_response = DownloadResponse(**response_data)

        logger.info(f"API Client: Successfully queued download for '{title}' (video_id: {video_id})")
        logger.debug(f"API Client: Download response: {download_response.model_dump()}")
        return download_response.model_dump()

    except ValidationError as e:
        log_request_response("POST", url, request_data, response, e)
        logger.error(f"Validation error during download request for '{title}': {e}")
        st.error(f"שגיאה בוולידציה של בקשת ההורדה: {e}")
        return None
    except requests.RequestException as e:
        log_request_response("POST", url, request_data, response, e)
        logger.error(f"Network error during download request for '{title}': {e}")
        st.error(f"שגיאת רשת בעת בקשת הורדה: {e}")
        return None
    except Exception as e:
        log_request_response("POST", url, request_data, response, e)
        logger.error(f"Unexpected error during download request for '{title}': {e}")
        st.error(f"שגיאה לא צפויה בבקשת הורדה: {e}")
        return None


@st.cache_data(ttl=60, show_spinner=False)  # Cache for 1 minute
def get_songs_library() -> List[Dict[str, Any]]:
    """
    Fetches the list of songs from the API.

    Returns:
        List of songs as dictionaries
    """
    logger.info("Fetching songs from API (cache miss)...")

    url = f"{API_BASE_URL}/songs"
    response = None

    try:
        log_request_response("GET", url)

        response = requests.get(
            url,
            timeout=StreamlitConfig.request_timeout
        )

        log_request_response("GET", url, None, response)
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        songs_response = SongsResponse(**response_data)

        songs = [song.model_dump() for song in songs_response.songs]
        logger.info(f"Successfully fetched {len(songs)} songs from the library.")
        return songs

    except ValidationError as e:
        log_request_response("GET", url, None, response, e)
        logger.error(f"Validation error while fetching songs: {e}")
        st.error(f"שגיאה בוולידציה של נתוני השירים: {e}")
        return []
    except requests.RequestException as e:
        log_request_response("GET", url, None, response, e)
        logger.error(f"Network error while fetching songs: {e}")
        st.error(f"שגיאת רשת בטעינת השירים: {e}")
        return []
    except Exception as e:
        log_request_response("GET", url, None, response, e)
        logger.error(f"Unexpected error while fetching songs: {e}")
        st.error(f"שגיאה לא צפויה בטעינת השירים: {e}")
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

    url = f"{API_BASE_URL}/songs/{video_id}/status"
    response = None

    try:
        log_request_response("GET", url)

        response = requests.get(
            url,
            timeout=StreamlitConfig.request_timeout
        )

        log_request_response("GET", url, None, response)
        response.raise_for_status()

        # Parse and validate response
        response_data = response.json()
        song_status = SongStatus(**response_data)

        return song_status.model_dump()

    except ValidationError as e:
        log_request_response("GET", url, None, response, e)
        logger.warning(f"Validation error while fetching status for video_id '{video_id}': {e}")
        return {}
    except requests.RequestException as e:
        # Don't show UI error for status checks, as it can be noisy, but log it.
        log_request_response("GET", url, None, response, e)
        logger.warning(f"Network error while fetching status for video_id '{video_id}': {e}")
        return {}
    except Exception as e:
        log_request_response("GET", url, None, response, e)
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

    url = f"{API_BASE_URL}/songs/{video_id}/download"
    response = None

    try:
        log_request_response("GET", url)

        response = requests.get(
            url,
            timeout=60  # Longer timeout for file download
        )

        log_request_response("GET", url, None, response)
        response.raise_for_status()

        logger.info(f"Successfully downloaded assets for video_id: {video_id} ({len(response.content)} bytes)")
        return response.content

    except requests.RequestException as e:
        log_request_response("GET", url, None, response, e)
        logger.error(f"Failed to download assets for video_id '{video_id}': {e}")
        st.error(f"שגיאה בהורדת קבצי הקריוקי: {e}")
        return None
    except Exception as e:
        log_request_response("GET", url, None, response, e)
        logger.error(f"Unexpected error downloading assets for video_id '{video_id}': {e}")
        st.error(f"שגיאה לא צפויה בהורדת קבצי הקריוקי: {e}")
        return None
