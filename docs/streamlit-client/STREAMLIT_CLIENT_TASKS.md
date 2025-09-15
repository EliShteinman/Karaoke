# Streamlit Client - רשימת משימות

## 🎯 תפקיד הסרוויס
ממשק משתמש אינטרקטיבי לחיפוש, הורדה ונגינת שירי קריוקי

---

## 📋 משימות פיתוח

### 1. הכנת סביבת הפיתוח
- [ ] יצירת תיקיית `services/streamlit-client/`
- [ ] הכנת `Dockerfile` לסרוויס
- [ ] יצירת `requirements.txt` עם Streamlit ו-audio libraries
- [ ] הגדרת משתני סביבה (API Server URL)

### 2. מבנה האפליקציה והניווט

#### Main App Structure
- [ ] יצירת `app/main.py` עם Streamlit entry point
- [ ] הגדרת page configuration וlayout
- [ ] יצירת sidebar לניווט בין עמודים
- [ ] מימוש session state management

```python
def main():
    st.set_page_config(
        page_title="Karaoke System",
        page_icon="🎤",
        layout="wide"
    )

    # Sidebar navigation
    pages = {
        "חיפוש שירים": "search",
        "הספריה שלי": "library",
        "נגן קריוקי": "player"
    }

    selected_page = st.sidebar.selectbox("בחר עמוד", list(pages.keys()))

    if pages[selected_page] == "search":
        show_search_page()
    elif pages[selected_page] == "library":
        show_library_page()
    elif pages[selected_page] == "player":
        show_player_page()
```

### 3. עמוד חיפוש שירים

#### Search Interface
- [ ] יצירת `app/pages/search.py`
- [ ] מימוש חיפוש עם input field וbutton
- [ ] הצגת תוצאות בgrid/list layout
- [ ] הוספת thumbnails ומטאדאטה לכל תוצאה

#### Components
- [ ] יצירת `app/components/search_form.py`:
```python
def render_search_form():
    with st.form("search_form"):
        query = st.text_input("חפש שיר או אמן", placeholder="לדוגמה: Rick Astley Never Gonna Give You Up")
        submit = st.form_submit_button("🔍 חפש")

        if submit and query:
            return query
    return None
```

- [ ] יצירת `app/components/search_results.py`:
```python
def render_search_results(results):
    for i, result in enumerate(results):
        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.image(result["thumbnail"], width=120)

        with col2:
            st.subheader(result["title"])
            st.text(f"ערוץ: {result['channel']}")
            st.text(f"אורך: {format_duration(result['duration'])}")

        with col3:
            if st.button(f"הורד", key=f"download_{result['video_id']}"):
                download_song(result)
                st.success("השיר נשלח לעיבוד!")
```

### 4. עמוד ספרייה

#### Library Interface
- [ ] יצירת `app/pages/library.py`
- [ ] קריאה ל-API עבור `GET /songs`
- [ ] הצגת שירים מוכנים בטבלה/grid
- [ ] סינון ומיון שירים
- [ ] כפתורי נגינה לכל שיר

```python
def show_library_page():
    st.header("🎵 הספרייה שלי")

    # Fetch ready songs
    songs = fetch_ready_songs()

    if not songs:
        st.info("עדיין אין שירים מוכנים. לך לחפש ולהוריד שירים!")
        return

    # Filter and sort options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("מיין לפי", ["תאריך", "שם", "אמן"])
    with col2:
        filter_text = st.text_input("סנן שירים")

    # Display songs
    for song in filter_songs(songs, filter_text, sort_by):
        render_song_card(song)
```

### 5. נגן קריוקי - עמוד הנגינה

#### Player Interface
- [ ] יצירת `app/pages/player.py`
- [ ] הצגת מטאדאטה השיר (כותרת, אמן, תמונה)
- [ ] player controls (play, pause, stop, seek)
- [ ] progress bar עם זמן נוכחי/כולל
- [ ] אזור הצגת כתוביות מסונכרן

#### Audio Player Component
- [ ] יצירת `app/components/player_controls.py`:
```python
def render_player_controls(audio_file):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("▶️ נגן"):
            st.session_state.playing = True

    with col2:
        if st.button("⏸️ השהה"):
            st.session_state.playing = False

    with col3:
        if st.button("⏹️ עצור"):
            st.session_state.playing = False
            st.session_state.position = 0

    with col4:
        volume = st.slider("עוצמה", 0, 100, 50)

    # Progress bar
    position = st.slider("מיקום", 0, st.session_state.duration, st.session_state.position)

    return {
        "playing": st.session_state.playing,
        "position": position,
        "volume": volume
    }
```

#### Lyrics Display Component
- [ ] יצירת `app/components/lyrics_display.py`:
```python
def render_lyrics(lyrics_data, current_time):
    # Parse LRC file
    lyrics_lines = parse_lrc_content(lyrics_data)

    # Find current and next lines
    current_line, next_line = find_current_lyrics(lyrics_lines, current_time)

    # Display lyrics with styling
    st.markdown("### כתוביות")

    # Previous lines (dimmed)
    for line in get_previous_lines(lyrics_lines, current_time, 2):
        st.markdown(f'<p style="opacity: 0.5">{line["text"]}</p>', unsafe_allow_html=True)

    # Current line (highlighted)
    if current_line:
        st.markdown(f'<p style="font-size: 1.5em; font-weight: bold; color: #ff6b6b">{current_line["text"]}</p>', unsafe_allow_html=True)

    # Next line (preview)
    if next_line:
        st.markdown(f'<p style="opacity: 0.7">{next_line["text"]}</p>', unsafe_allow_html=True)
```

### 6. שירותי API ותקשורת - קלט/פלט מפורט

#### API Client - מפרט קריאות
**POST /search - חיפוש שירים**
```python
# קלט
query = "rick astley never gonna give you up"
request = {"query": query}

# פלט
response = {
    "results": [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Rick Astley - Never Gonna Give You Up",
            "channel": "RickAstleyVEVO",
            "duration": 213,
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "published_at": "2009-10-25T09:57:33Z"
        }
    ]
}
```

**POST /download - הורדת שיר**
```python
# קלט
video_data = {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "channel": "RickAstleyVEVO",
    "duration": 213,
    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}

# פלט
response = {
    "status": "accepted",
    "video_id": "dQw4w9WgXcQ",
    "message": "Song queued for processing"
}
```

**GET /songs - רשימת שירים מוכנים**
```python
# פלט
response = {
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

**GET /songs/{video_id}/status - סטטוס שיר**
```python
# פלט
response = {
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

**GET /songs/{video_id}/download - הורדת קבצים**
```python
# פלט: ZIP file עם:
# - vocals_removed.mp3 (מוזיקה ללא ווקאל)
# - lyrics.lrc (כתוביות עם timestamps)
```

- [ ] יצירת `app/services/api_client.py` עם כל הפונקציות
- [ ] טיפול בשגיאות HTTP ובvalidation
- [ ] timeout ו-retry logic לכל קריאה

#### File Management - עיבוד קבצי ZIP
**קלט:** ZIP content מ-API Server

**פלט:** קבצים מחולצים
```python
# מבנה הקבצים לאחר חילוץ:
{
    "audio": "/tmp/songs/dQw4w9WgXcQ/vocals_removed.mp3",
    "lyrics": "/tmp/songs/dQw4w9WgXcQ/lyrics.lrc"
}
```

- [ ] יצירת `app/services/file_manager.py`:
```python
def extract_song_files(zip_content, video_id):
    """Extract ZIP and return audio and lyrics paths"""
    import zipfile
    import io

    extract_dir = f"/tmp/songs/{video_id}"
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
        zip_file.extractall(extract_dir)

    return {
        "audio": f"{extract_dir}/vocals_removed.mp3",
        "lyrics": f"{extract_dir}/lyrics.lrc"
    }
```

### 7. עיבוד אודיו וכתוביות

#### Audio Processing
- [ ] יצירת `app/services/audio_player.py`:
```python
def load_audio_file(audio_path):
    """Load audio and return duration, waveform data"""
    from pydub import AudioSegment

    audio = AudioSegment.from_mp3(audio_path)
    duration = len(audio) / 1000.0  # seconds

    return {
        "duration": duration,
        "audio_data": audio,
        "sample_rate": audio.frame_rate
    }

def play_audio_segment(audio_data, start_time, end_time):
    """Play specific segment of audio"""
    start_ms = int(start_time * 1000)
    end_ms = int(end_time * 1000)
    segment = audio_data[start_ms:end_ms]

    # Save temporary file and play
    temp_file = f"/tmp/temp_audio_{int(time.time())}.mp3"
    segment.export(temp_file, format="mp3")

    return temp_file
```

#### LRC Parser - עיבוד כתוביות
**קלט:** תוכן קובץ LRC
```lrc
[ar:Rick Astley]
[ti:Never Gonna Give You Up]
[00:00.50]We're no strangers to love
[00:04.15]You know the rules and so do I
[00:08.20]A full commitment's what I'm thinking of
```

**פלט:** רשימת כתוביות מתוזמנות
```python
[
    {"time": 0.5, "text": "We're no strangers to love"},
    {"time": 4.15, "text": "You know the rules and so do I"},
    {"time": 8.2, "text": "A full commitment's what I'm thinking of"}
]
```

- [ ] יצירת `app/services/lrc_parser.py`:
```python
def parse_lrc_file(lrc_content):
    """Parse LRC file and return timed lyrics"""
    lines = []

    for line in lrc_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('[ar:') or line.startswith('[ti:'):
            continue

        # Extract timestamp [mm:ss.xx]
        if line.startswith('[') and ']' in line:
            timestamp_str = line[1:line.index(']')]
            text = line[line.index(']') + 1:].strip()

            # Convert to seconds
            try:
                parts = timestamp_str.split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                total_seconds = minutes * 60 + seconds

                lines.append({
                    "time": total_seconds,
                    "text": text
                })
            except:
                continue

    return sorted(lines, key=lambda x: x["time"])

def find_current_line(lyrics, current_time):
    """Find the current lyrics line based on time"""
    for i, line in enumerate(lyrics):
        if i == len(lyrics) - 1:  # Last line
            return line

        next_line_time = lyrics[i + 1]["time"]
        if line["time"] <= current_time < next_line_time:
            return line

    return None
```

### 8. State Management וSession

#### Session State Manager
- [ ] יצירת `app/utils/session_state.py`:
```python
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "current_song": None,
        "playing": False,
        "position": 0.0,
        "duration": 0.0,
        "volume": 50,
        "lyrics_data": None,
        "audio_file": None,
        "search_results": [],
        "ready_songs": []
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def update_playback_position():
    """Update current playback position"""
    if st.session_state.playing:
        # This would be called periodically
        current_time = time.time()
        if "playback_start_time" in st.session_state:
            elapsed = current_time - st.session_state.playback_start_time
            st.session_state.position = min(
                st.session_state.position + elapsed,
                st.session_state.duration
            )
        st.session_state.playback_start_time = current_time
```

### 9. UI/UX וסטיילינג

#### Custom Styling
- [ ] יצירת `app/styles/custom.css`:
```css
/* Player styling */
.player-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
}

.lyrics-container {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    padding: 20px;
    height: 400px;
    overflow-y: auto;
}

.current-lyric {
    font-size: 1.5em !important;
    color: #ff6b6b !important;
    font-weight: bold !important;
    text-align: center;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}
```

- [ ] הטמעת CSS ב-Streamlit עם `st.markdown()`

#### Responsive Design
- [ ] אופטימיזציה למובייל וטאבלט
- [ ] הגדרת columns ורווחים
- [ ] טיפוח UX intuitive

### 10. מעקב סטטוס והתראות

#### Status Monitoring
- [ ] polling אוטומטי לסטטוס שירים בעיבוד
- [ ] progress bars לשירים שבהורדה
- [ ] התראות בזמן אמת על שירים מוכנים

```python
def monitor_song_status(video_id):
    """Poll song status until ready"""
    with st.spinner("מעבד את השיר..."):
        while True:
            status = api_client.get_song_status(video_id)

            if status["progress"]["files_ready"]:
                st.success("השיר מוכן לנגינה!")
                break

            # Show progress
            progress_text = []
            if status["progress"]["download"]:
                progress_text.append("✅ הורדה")
            if status["progress"]["audio_processing"]:
                progress_text.append("✅ עיבוד אודיו")
            if status["progress"]["transcription"]:
                progress_text.append("✅ תמלול")

            st.info(" | ".join(progress_text))
            time.sleep(5)
```

### 11. בדיקות ואיכות

#### Testing Strategy
- [ ] Unit tests לפונקציות utility
- [ ] בדיקת integration עם API
- [ ] בדיקת UI components
- [ ] בדיקת זרימת משתמש E2E

#### Performance Optimization
- [ ] cache של API responses
- [ ] lazy loading של אודיו files
- [ ] אופטימיזציה של re-renders
- [ ] ניהול זיכרון לאודיו files

---

## 🔧 טכנולוגיות נדרשות

### Core Framework
- **streamlit** - Web framework
- **requests** - HTTP client לAPI
- **pandas** - Data manipulation אופציונלי

### Audio & Media
- **pydub** - Audio processing
- **streamlit-audio-recorder** - Audio input אופציונלי
- **matplotlib/plotly** - Visualization אופציונלי

### File Handling
- **zipfile** - ZIP extraction
- **io** - Stream handling
- **tempfile** - Temporary file management

---

## 📦 Dependencies מוערכות

```txt
streamlit==1.28.1
requests==2.31.0
pydub==0.25.1
pandas==2.1.3
plotly==5.17.0
streamlit-audio-recorder==0.0.8
python-dotenv==1.0.0
Pillow==10.1.0
```

---

## 🚀 הערות חשובות

### Streamlit Limitations
- אין real-time audio playback built-in
- צריך workarounds לאודיו sync
- Session state נמחק בrefresh

### Audio Playback Solutions
```python
# Option 1: HTML5 audio with JavaScript
def render_audio_player(audio_path):
    audio_html = f'''
    <audio id="audio-player" controls style="width: 100%">
        <source src="{audio_path}" type="audio/mpeg">
    </audio>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)

# Option 2: Streamlit native (limited)
def render_native_audio(audio_file):
    st.audio(audio_file)
```

### Real-time Lyrics Sync
זה המאתגר ביותר בStreamlit:
- אין built-in real-time updates
- צריך JavaScript injection או polling

### File Management
```python
# Clean up temporary files
def cleanup_temp_files():
    temp_dir = "/tmp/songs"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
```

### Docker Considerations
```dockerfile
# Audio libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

השירות הזה הוא המורכב ביותר מבחינת UX - צריך יצירתיות לעקיפת מגבלות Streamlit!