# Streamlit Client - סכמות קלט ופלט

## סקירה כללית
מסמך זה מכיל את הסכמות המלאות לכל נקודות הקלט והפלט של הלקוח Streamlit.

**עיקרון חשוב בנוגע לתקשורת:**
- הלקוח מתקשר **אך ורק** עם ה-API Server
- **אין גישה ישירה** לקפקא, אלסטיק או shared storage
- כל המידע מתקבל דרך REST API endpoints

---

## 1. קלט מהמשתמש - חיפוש שירים

### Streamlit Input Components
**עמוד:** Search Page

**Schema קלט (Streamlit form):**
```python
# Streamlit component
search_query = st.text_input(
    "חפש שיר או אמן",
    placeholder="לדוגמה: Rick Astley Never Gonna Give You Up",
    max_chars=200
)
search_button = st.form_submit_button("🔍 חפש")

# Validation
class SearchInputSchema:
    def validate_search_query(query: str) -> bool:
        if not query or len(query.strip()) < 2:
            st.error("נא להזין לפחות 2 תווים לחיפוש")
            return False
        if len(query) > 200:
            st.error("שאילתת החיפוש ארוכה מדי (מקסימום 200 תווים)")
            return False
        return True
```

**Schema Python לקלט:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchInput:
    query: str
    user_session_id: Optional[str] = None
    timestamp: Optional[str] = None

    def to_api_request(self) -> dict:
        """Convert to API request format"""
        return {"query": self.query.strip()}
```

---

## 2. פלט לAPI Server - בקשת חיפוש

### HTTP Request to API Server
**Endpoint:** `POST /search`

**Schema בקשה:**
```python
import requests
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def search_songs(self, query: str) -> Dict[str, Any]:
        """Search for songs via API Server"""
        payload = {"query": query}

        try:
            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("החיפוש נכשל - זמן ההמתנה פג")
            return {"results": []}
        except requests.exceptions.ConnectionError:
            st.error("אין חיבור לשרת")
            return {"results": []}
```

**פורמט הבקשה (JSON):**
```json
{
  "query": "rick astley never gonna give you up"
}
```

---

## 3. קלט מAPI Server - תוצאות חיפוש

### HTTP Response from API Server
**Schema תגובה:**
```json
{
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
      "channel": "RickAstleyVEVO",
      "duration": 213,
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "published_at": "2009-10-25T09:57:33Z"
    }
  ]
}
```

**Schema Python למידע שהתקבל:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SearchResultItem(BaseModel):
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$')
    title: str = Field(..., min_length=1, max_length=500)
    channel: str = Field(..., min_length=1, max_length=200)
    duration: int = Field(..., gt=0)
    thumbnail: str = Field(..., regex=r'^https?://.+')
    published_at: str

    def format_duration(self) -> str:
        """Convert seconds to MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_artist_name(self) -> str:
        """Extract artist name from title"""
        if " - " in self.title:
            return self.title.split(" - ")[0]
        return self.channel

class SearchResponse(BaseModel):
    results: List[SearchResultItem]

    def is_empty(self) -> bool:
        return len(self.results) == 0
```

---

## 4. פלט למשתמש - הצגת תוצאות חיפוש

### Streamlit Display Components
**עמוד:** Search Page

**Schema תצוגה:**
```python
def render_search_results(search_response: SearchResponse):
    """Render search results in Streamlit"""

    if search_response.is_empty():
        st.info("לא נמצאו תוצאות לחיפוש זה. נסה מילות חיפוש אחרות.")
        return

    st.write(f"נמצאו {len(search_response.results)} תוצאות:")

    for i, result in enumerate(search_response.results):
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                # Thumbnail image
                st.image(result.thumbnail, width=120)

            with col2:
                # Song metadata
                st.subheader(result.title)
                st.text(f"ערוץ: {result.channel}")
                st.text(f"אורך: {result.format_duration()}")
                st.text(f"פורסם: {format_publish_date(result.published_at)}")

            with col3:
                # Download button
                download_key = f"download_{result.video_id}_{i}"
                if st.button("📥 הורד", key=download_key):
                    return result  # Return selected song for download

        st.divider()

    return None

def format_publish_date(date_str: str) -> str:
    """Format ISO date to Hebrew readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str
```

---

## 5. קלט מהמשתמש - בחירת שיר להורדה

### User Selection Input
**Schema לבחירת שיר:**
```python
@dataclass
class SongSelectionInput:
    selected_result: SearchResultItem
    user_action: str = "download"
    timestamp: str = None

    def to_download_request(self) -> dict:
        """Convert to API download request"""
        return {
            "video_id": self.selected_result.video_id,
            "title": self.selected_result.title,
            "channel": self.selected_result.channel,
            "duration": self.selected_result.duration,
            "thumbnail": self.selected_result.thumbnail
        }

# Streamlit component handler
def handle_song_selection(selected_result: SearchResultItem):
    """Handle user song selection"""
    with st.spinner(f"מוריד את השיר: {selected_result.title}"):
        download_response = api_client.download_song(
            selected_result.to_download_request()
        )

        if download_response.get("status") == "accepted":
            st.success("השיר נשלח לעיבוד!")

            # Save to session state for status monitoring
            if "downloading_songs" not in st.session_state:
                st.session_state.downloading_songs = []

            st.session_state.downloading_songs.append({
                "video_id": selected_result.video_id,
                "title": selected_result.title,
                "start_time": datetime.now().isoformat()
            })
        else:
            st.error("שגיאה בהורדת השיר. נסה שוב.")
```

---

## 6. פלט לAPI Server - בקשת הורדה

### HTTP Request for Download
**Endpoint:** `POST /download`

**Schema בקשה:**
```python
def download_song(self, song_data: dict) -> Dict[str, Any]:
    """Request song download via API Server"""

    # Validate input
    required_fields = ["video_id", "title", "channel", "duration", "thumbnail"]
    for field in required_fields:
        if field not in song_data:
            raise ValueError(f"Missing required field: {field}")

    try:
        response = requests.post(
            f"{self.base_url}/download",
            json=song_data,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 409:  # Conflict - song already exists
            st.warning("השיר כבר קיים במערכת")
        elif response.status_code == 400:  # Bad request
            st.error("נתונים לא תקינים")
        else:
            st.error(f"שגיאה בהורדת השיר: {response.status_code}")
        return {"status": "error"}
```

**פורמט הבקשה (JSON):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

---

## 7. קלט מAPI Server - אישור הורדה

### Download Confirmation Response
**Schema תגובה:**
```json
{
  "status": "accepted",
  "video_id": "dQw4w9WgXcQ",
  "message": "Song queued for processing"
}
```

**Schema Python:**
```python
class DownloadResponse(BaseModel):
    status: Literal["accepted", "error"]
    video_id: str
    message: str
    error_code: Optional[str] = None

def handle_download_response(response: DownloadResponse):
    """Handle download response from API"""
    if response.status == "accepted":
        st.success(f"✅ {response.message}")

        # Start status monitoring
        start_status_monitoring(response.video_id)

    elif response.status == "error":
        st.error(f"❌ שגיאה: {response.message}")
        if response.error_code == "SONG_ALREADY_EXISTS":
            st.info("השיר כבר קיים. בדוק בספריה שלך.")
```

---

## 8. מעקב סטטוס - Polling

### Status Monitoring Loop
**Endpoint:** `GET /songs/{video_id}/status`

**Schema פניה:**
```python
async def monitor_song_status(video_id: str):
    """Monitor song processing status"""

    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    while True:
        try:
            status_response = api_client.get_song_status(video_id)

            with progress_placeholder.container():
                render_progress_bar(status_response["progress"])

            with status_placeholder.container():
                render_status_info(status_response)

            # Check if ready
            if status_response["progress"]["files_ready"]:
                st.success("🎉 השיר מוכן לנגינה!")
                # Update library
                refresh_library()
                break

            # Check for failure
            if status_response["status"] == "failed":
                st.error("💥 העיבוד נכשל")
                break

            time.sleep(5)  # Poll every 5 seconds

        except Exception as e:
            st.error(f"שגיאה במעקב סטטוס: {e}")
            break

def render_progress_bar(progress: dict):
    """Render processing progress"""
    steps = [
        ("download", "הורדה", progress["download"]),
        ("audio_processing", "עיבוד אודיו", progress["audio_processing"]),
        ("transcription", "תמלול", progress["transcription"]),
        ("files_ready", "מוכן", progress["files_ready"])
    ]

    completed_steps = sum(1 for _, _, completed in steps if completed)
    progress_percentage = (completed_steps / len(steps)) * 100

    st.progress(progress_percentage / 100)

    status_text = " | ".join([
        f"{'✅' if completed else '⏳'} {label}"
        for _, label, completed in steps
    ])

    st.text(status_text)
```

**Schema תגובת סטטוס:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "processing",
  "progress": {
    "download": true,
    "audio_processing": true,
    "transcription": true,
    "files_ready": true
  }
}
```

---

## 9. קלט מAPI Server - רשימת שירים מוכנים

### Library Page Data Fetch
**Endpoint:** `GET /songs`

**Schema תגובה:**
```json
{
  "songs": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "artist": "Rick Astley",
      "status": "processing",
      "created_at": "2025-09-15T10:30:00Z",
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "duration": 213,
      "files_ready": true
    }
  ]
}
```

**Schema Python:**
```python
class LibrarySong(BaseModel):
    video_id: str
    title: str
    artist: str
    status: str
    created_at: str
    thumbnail: str
    duration: int
    files_ready: bool

    def format_created_date(self) -> str:
        """Format creation date to Hebrew"""
        try:
            dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return self.created_at

class LibraryResponse(BaseModel):
    songs: List[LibrarySong]

    def get_songs_by_status(self, ready_only: bool = True) -> List[LibrarySong]:
        """Filter songs by readiness"""
        if ready_only:
            return [song for song in self.songs if song.files_ready]
        return self.songs

    def sort_songs(self, sort_by: str = "created_at", reverse: bool = True) -> List[LibrarySong]:
        """Sort songs by different criteria"""
        if sort_by == "title":
            return sorted(self.songs, key=lambda x: x.title, reverse=reverse)
        elif sort_by == "artist":
            return sorted(self.songs, key=lambda x: x.artist, reverse=reverse)
        elif sort_by == "duration":
            return sorted(self.songs, key=lambda x: x.duration, reverse=reverse)
        else:  # created_at
            return sorted(self.songs, key=lambda x: x.created_at, reverse=reverse)
```

---

## 10. פלט למשתמש - הצגת ספרייה

### Library Display Components
**עמוד:** Library Page

**Schema תצוגה:**
```python
def render_library_page():
    """Render library page with ready songs"""

    st.header("🎵 הספרייה שלי")

    # Fetch songs
    library_data = api_client.get_ready_songs()
    library = LibraryResponse(**library_data)

    if not library.songs:
        st.info("עדיין אין שירים מוכנים. לך לחפש ולהוריד שירים!")
        return

    # Filter and sort controls
    col1, col2, col3 = st.columns(3)

    with col1:
        sort_by = st.selectbox("מיין לפי", ["תאריך", "שם", "אמן", "אורך"])

    with col2:
        filter_text = st.text_input("סנן שירים", placeholder="חפש בספרייה...")

    with col3:
        show_all = st.checkbox("הצג גם שירים בעיבוד", value=False)

    # Process songs
    songs = library.get_songs_by_status(ready_only=not show_all)

    # Apply filter
    if filter_text:
        songs = [
            song for song in songs
            if filter_text.lower() in song.title.lower()
            or filter_text.lower() in song.artist.lower()
        ]

    # Apply sort
    sort_mapping = {
        "תאריך": "created_at",
        "שם": "title",
        "אמן": "artist",
        "אורך": "duration"
    }
    songs = library.sort_songs(sort_mapping[sort_by])

    # Display songs
    for song in songs:
        render_song_card(song)

def render_song_card(song: LibrarySong):
    """Render individual song card"""

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.image(song.thumbnail, width=100)

        with col2:
            st.subheader(song.title)
            st.text(f"אמן: {song.artist}")
            st.text(f"אורך: {format_duration(song.duration)}")
            st.text(f"נוסף: {song.format_created_date()}")

            if not song.files_ready:
                st.warning("🔄 בעיבוד...")

        with col3:
            if song.files_ready:
                play_button_key = f"play_{song.video_id}"
                if st.button("🎤 נגן", key=play_button_key):
                    # Save selected song to session state
                    st.session_state.selected_song = song
                    st.session_state.current_page = "player"
                    st.rerun()

        st.divider()
```

---

## 11. קלט מAPI Server - הורדת קבצי השיר

### Download Song Files
**Endpoint:** `GET /songs/{video_id}/download`

**Schema בקשה:**
```python
def download_song_files(self, video_id: str) -> bytes:
    """Download song files as ZIP"""

    try:
        response = requests.get(
            f"{self.base_url}/songs/{video_id}/download",
            timeout=30,
            stream=True
        )
        response.raise_for_status()

        # Validate content type
        if response.headers.get('content-type') != 'application/zip':
            raise ValueError("Expected ZIP file")

        return response.content

    except requests.exceptions.Timeout:
        st.error("זמן ההורדה פג. נסה שוב.")
        return None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            st.error("השיר לא נמצא")
        elif response.status_code == 425:  # Too Early
            st.warning("השיר עדיין בעיבוד")
        else:
            st.error(f"שגיאה בהורדת השיר: {response.status_code}")
        return None
```

**פורמט תגובה:**
- **Content-Type:** `application/zip`
- **ZIP Structure:**
  ```
  {video_id}_karaoke.zip
  ├── vocals_removed.mp3    # מוזיקה ללא ווקאל
  └── lyrics.lrc           # כתוביות עם timestamps
  ```

---

## 12. עיבוד קבצים - חילוץ ZIP

### File Extraction and Processing
**Schema עיבוד קבצים:**
```python
import zipfile
import io
import tempfile
import os

class SongFilesProcessor:
    def __init__(self, temp_dir: str = "/tmp/karaoke_songs"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def extract_song_files(self, zip_content: bytes, video_id: str) -> dict:
        """Extract ZIP and return file paths"""

        song_dir = os.path.join(self.temp_dir, video_id)
        os.makedirs(song_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                # Extract all files
                zip_file.extractall(song_dir)

                # Find audio and lyrics files
                extracted_files = os.listdir(song_dir)

                audio_file = None
                lyrics_file = None

                for file_name in extracted_files:
                    if file_name.endswith('.mp3'):
                        audio_file = os.path.join(song_dir, file_name)
                    elif file_name.endswith('.lrc'):
                        lyrics_file = os.path.join(song_dir, file_name)

                if not audio_file or not lyrics_file:
                    raise ValueError("Missing audio or lyrics file in ZIP")

                return {
                    "audio_path": audio_file,
                    "lyrics_path": lyrics_file,
                    "song_dir": song_dir
                }

        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")
        except Exception as e:
            raise ValueError(f"Failed to extract files: {e}")

    def cleanup_song_files(self, video_id: str):
        """Clean up temporary files"""
        song_dir = os.path.join(self.temp_dir, video_id)
        if os.path.exists(song_dir):
            import shutil
            shutil.rmtree(song_dir)

# Usage in Streamlit
@st.cache_data
def load_song_files(video_id: str) -> dict:
    """Load and cache song files"""

    if f"song_files_{video_id}" in st.session_state:
        return st.session_state[f"song_files_{video_id}"]

    # Download ZIP from API
    zip_content = api_client.download_song_files(video_id)
    if not zip_content:
        return None

    # Extract files
    processor = SongFilesProcessor()
    files = processor.extract_song_files(zip_content, video_id)

    # Cache in session state
    st.session_state[f"song_files_{video_id}"] = files

    return files
```

---

## 13. נגן קריוקי - עיבוד אודיו וכתוביות

### Audio Processing for Player
**Schema עיבוד אודיו:**
```python
from pydub import AudioSegment
import streamlit as st

class AudioProcessor:
    def load_audio_file(self, audio_path: str) -> dict:
        """Load audio file and extract metadata"""

        try:
            audio = AudioSegment.from_mp3(audio_path)

            return {
                "duration_seconds": len(audio) / 1000.0,
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "file_size": os.path.getsize(audio_path),
                "audio_data": audio
            }
        except Exception as e:
            st.error(f"שגיאה בטעינת קובץ האודיו: {e}")
            return None

    def create_audio_segments(self, audio_data: AudioSegment, segment_length: float = 1.0) -> list:
        """Create audio segments for playback"""
        segments = []
        duration_ms = len(audio_data)
        segment_ms = int(segment_length * 1000)

        for start_ms in range(0, duration_ms, segment_ms):
            end_ms = min(start_ms + segment_ms, duration_ms)
            segment = audio_data[start_ms:end_ms]
            segments.append({
                "start_time": start_ms / 1000.0,
                "end_time": end_ms / 1000.0,
                "audio_segment": segment
            })

        return segments
```

### Lyrics Processing
**Schema עיבוד כתוביות:**
```python
import re
from typing import List, Tuple, Optional

class LyricsProcessor:
    def parse_lrc_file(self, lyrics_path: str) -> List[dict]:
        """Parse LRC file and return timed lyrics"""

        with open(lyrics_path, 'r', encoding='utf-8') as file:
            content = file.read()

        lyrics_lines = []

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Skip metadata lines
            if line.startswith('[ar:') or line.startswith('[ti:') or line.startswith('[al:'):
                continue

            # Parse timed lyrics [mm:ss.xx]text
            match = re.match(r'\[(\d{2}):(\d{2})\.(\d{2})\](.*)', line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                centiseconds = int(match.group(3))
                text = match.group(4).strip()

                total_seconds = minutes * 60 + seconds + centiseconds / 100.0

                lyrics_lines.append({
                    "time": total_seconds,
                    "text": text,
                    "minutes": minutes,
                    "seconds": seconds,
                    "centiseconds": centiseconds
                })

        return sorted(lyrics_lines, key=lambda x: x["time"])

    def find_current_lyrics(self, lyrics: List[dict], current_time: float) -> Tuple[Optional[dict], Optional[dict]]:
        """Find current and next lyrics line"""

        current_line = None
        next_line = None

        for i, line in enumerate(lyrics):
            if i == len(lyrics) - 1:  # Last line
                if line["time"] <= current_time:
                    current_line = line
                break

            next_line_time = lyrics[i + 1]["time"]

            if line["time"] <= current_time < next_line_time:
                current_line = line
                next_line = lyrics[i + 1]
                break
            elif current_time < line["time"]:
                # Current time is before this line
                next_line = line
                break

        return current_line, next_line

    def get_context_lyrics(self, lyrics: List[dict], current_time: float,
                          previous_lines: int = 2, next_lines: int = 2) -> dict:
        """Get lyrics context (previous, current, next lines)"""

        current_line, next_line = self.find_current_lyrics(lyrics, current_time)

        if not current_line:
            return {
                "previous": [],
                "current": None,
                "next": lyrics[:next_lines] if lyrics else []
            }

        current_index = lyrics.index(current_line)

        return {
            "previous": lyrics[max(0, current_index - previous_lines):current_index],
            "current": current_line,
            "next": lyrics[current_index + 1:current_index + 1 + next_lines]
        }
```

---

## 14. פלט למשתמש - נגן קריוקי

### Karaoke Player Interface
**עמוד:** Player Page

**Schema רכיבי הנגן:**
```python
def render_karaoke_player(song: LibrarySong):
    """Render full karaoke player interface"""

    st.header(f"🎤 {song.title}")
    st.subheader(f"אמן: {song.artist}")

    # Load song files
    song_files = load_song_files(song.video_id)
    if not song_files:
        st.error("לא ניתן לטעון את קבצי השיר")
        return

    # Load audio and lyrics
    audio_processor = AudioProcessor()
    lyrics_processor = LyricsProcessor()

    audio_data = audio_processor.load_audio_file(song_files["audio_path"])
    lyrics_data = lyrics_processor.parse_lrc_file(song_files["lyrics_path"])

    if not audio_data or not lyrics_data:
        st.error("שגיאה בטעינת נתוני השיר")
        return

    # Player controls
    render_player_controls(audio_data, song.video_id)

    # Progress bar
    current_time = st.session_state.get(f"position_{song.video_id}", 0.0)
    duration = audio_data["duration_seconds"]

    progress = st.slider(
        "התקדמות השיר",
        min_value=0.0,
        max_value=duration,
        value=current_time,
        step=0.1,
        format="%.1f",
        key=f"progress_{song.video_id}"
    )

    # Update current time
    st.session_state[f"position_{song.video_id}"] = progress

    # Time display
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"זמן נוכחי: {format_time(progress)}")
    with col2:
        st.text(f"זמן כולל: {format_time(duration)}")

    # Lyrics display
    render_lyrics_display(lyrics_data, progress)

def render_player_controls(audio_data: dict, video_id: str):
    """Render player control buttons"""

    col1, col2, col3, col4 = st.columns(4)

    playing_key = f"playing_{video_id}"
    position_key = f"position_{video_id}"

    with col1:
        if st.button("▶️ נגן", key=f"play_{video_id}"):
            st.session_state[playing_key] = True
            st.session_state[f"play_start_time_{video_id}"] = time.time()

    with col2:
        if st.button("⏸️ השהה", key=f"pause_{video_id}"):
            st.session_state[playing_key] = False

    with col3:
        if st.button("⏹️ עצור", key=f"stop_{video_id}"):
            st.session_state[playing_key] = False
            st.session_state[position_key] = 0.0

    with col4:
        volume = st.slider("עוצמה", 0, 100, 70, key=f"volume_{video_id}")

    # Auto-update position if playing
    if st.session_state.get(playing_key, False):
        update_playback_position(video_id)

def render_lyrics_display(lyrics_data: List[dict], current_time: float):
    """Render synchronized lyrics display"""

    lyrics_processor = LyricsProcessor()
    context = lyrics_processor.get_context_lyrics(lyrics_data, current_time)

    st.markdown("### כתוביות")

    # Create lyrics container
    with st.container():
        # Previous lines (dimmed)
        for line in context["previous"]:
            st.markdown(
                f'<p style="opacity: 0.5; color: #888; text-align: center; margin: 5px 0;">'
                f'{line["text"]}</p>',
                unsafe_allow_html=True
            )

        # Current line (highlighted)
        if context["current"]:
            st.markdown(
                f'<p style="font-size: 1.8em; font-weight: bold; color: #ff6b6b; '
                f'text-align: center; margin: 15px 0; animation: pulse 1s infinite;">'
                f'{context["current"]["text"]}</p>',
                unsafe_allow_html=True
            )

        # Next lines (preview)
        for line in context["next"]:
            st.markdown(
                f'<p style="opacity: 0.7; color: #666; text-align: center; margin: 5px 0;">'
                f'{line["text"]}</p>',
                unsafe_allow_html=True
            )

def format_time(seconds: float) -> str:
    """Format seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def update_playback_position(video_id: str):
    """Update playback position for playing songs"""

    playing_key = f"playing_{video_id}"
    position_key = f"position_{video_id}"
    start_time_key = f"play_start_time_{video_id}"

    if st.session_state.get(playing_key, False):
        current_time = time.time()
        start_time = st.session_state.get(start_time_key, current_time)
        elapsed = current_time - start_time

        current_position = st.session_state.get(position_key, 0.0)
        new_position = current_position + elapsed

        st.session_state[position_key] = new_position
        st.session_state[start_time_key] = current_time

        # Auto-refresh for real-time updates
        time.sleep(0.1)
        st.rerun()
```

---

## 15. עדכון דוקומנטציה נדרש

### הבהרה בדוקומנטציה הקיימת:

**עקרון מרכזי שיש להדגיש:**
> **חשוב:** הלקוח Streamlit מתקשר **אך ורק** עם ה-API Server. אין גישה ישירה לכלום מלבד ה-API endpoints המוגדרים. כל המידע - כולל קבצי השמע והכתוביות - מתקבל דרך REST API.

**מודל תקשורת:**
1. ✅ **HTTP Requests** → API Server endpoints
2. ✅ **File Downloads** → דרך API Server (ZIP files)
3. ✅ **Status Updates** → polling API Server
4. ❌ **אין גישה ישירה** לקפקא, אלסטיק או shared storage

### תזרים המידע המלא:
```
1. User Input → Streamlit forms/components
2. Streamlit → API Server (HTTP requests)
3. API Server → Streamlit (JSON responses/ZIP files)
4. Streamlit → User Interface (rendered components)
```

זה האדריכלות הנכונה למערכת - הלקוח נקי ופשוט, כל המורכבות ב-backend!