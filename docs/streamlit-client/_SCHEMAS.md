# Streamlit Client - סכמות קלט ופלט

## סקירה כללית
Streamlit Client מספק ממשק משתמש מלא לחיפוש שירים, מעקב אחר התקדמות העיבוד, והפעלת נגן קריוקי מתקדם. הלקוח מתקשר בלעדית עם API Server דרך HTTP requests ולא ניגש ישירות לשירותי התשתית.

## קלט (Inputs)

### קלט מהמשתמש

#### חיפוש שירים
**ממשק:** טופס חיפוש טקסט
**פורמט:** מחרוזת חיפוש חופשית
**דוגמה:** "rick astley never gonna give you up"
**אורך מקסימלי:** 200 תווים

#### בחירת שיר להורדה
**ממשק:** כפתור "הורד" ברשימת תוצאות
**מידע נדרש:**
- `video_id`: מזהה יוטיוב
- `title`: כותרת השיר
- `channel`: שם הערוץ
- `duration`: משך בשניות
- `thumbnail`: קישור לתמונה

#### בקרות נגן
**ממשק:** בקרות אודיו אינטראקטיביות
**פונקציות:**
- Play/Pause
- Stop
- Seek (דילוג לזמן מסוים)
- Volume Control

### בקשות HTTP ל-API Server

#### חיפוש שירים
**Endpoint:** `POST /search`
**תדירות:** כל בקשת חיפוש מהמשתמש

**מבנה הבקשה:**
```json
{
  "query": "rick astley never gonna give you up"
}
```

#### בקשת הורדת שיר
**Endpoint:** `POST /download`
**תדירות:** כל לחיצה על "הורד"

**מבנה הבקשה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

#### רשימת שירים מוכנים
**Endpoint:** `GET /songs`
**תדירות:** טעינה ראשונית + רענון ידני

#### מעקב אחר סטטוס
**Endpoint:** `GET /songs/{video_id}/status`
**תדירות:** Polling כל 5 שניות עד להשלמה

#### הורדת קבצי קריוקי
**Endpoint:** `GET /songs/{video_id}/download`
**תדירות:** לחיצה על "הפעל קריוקי"

## פלט (Outputs)

### תצוגה למשתמש

#### רשימת תוצאות חיפוש
**פורמט:** גריד של כרטיסי שירים
**מידע מוצג:**
```python
search_result_display = {
    "thumbnail": "תמונת תצוגה מקדימה",
    "title": "Rick Astley - Never Gonna Give You Up",
    "channel": "RickAstleyVEVO",
    "duration": "3:33",           # המרה מ-213 שניות
    "published": "2009",          # שנה בלבד
    "download_button": "כפתור הורד"
}
```

#### מעקב התקדמות עיבוד
**פורמט:** Progress Bar עם שלבים
**שלבי ההתקדמות:**
1. ⏳ הורדה מיוטיוב
2. 🎵 עיבוד אודיו (הסרת ווקאל)
3. 📝 תמלול וכתוביות
4. ✅ מוכן לנגינה

**תצוגת סטטוס:**
```python
progress_display = {
    "overall_status": "בעיבוד...",
    "download": "✅ הושלם",
    "audio_processing": "🔄 בתהליך",
    "transcription": "⏳ ממתין",
    "estimated_time": "עוד ~2 דקות"
}
```

#### ספריית שירים
**פורמט:** רשימה של שירים מוכנים
**מידע מוצג:**
```python
song_library_item = {
    "thumbnail": "תמונה קטנה",
    "title": "Never Gonna Give You Up",
    "artist": "Rick Astley",
    "duration": "3:33",
    "created_date": "15/09/2025",
    "play_button": "▶️ הפעל קריוקי"
}
```

### נגן קריוקי - ממשק משתמש

#### מטא-דאטה
**מיקום:** חלק עליון של הנגן
```python
metadata_display = {
    "song_title": "Never Gonna Give You Up",
    "artist_name": "Rick Astley",
    "album_art": "תמונת השיר (גדולה)",
    "duration": "3:33",
    "current_time": "1:24"
}
```

#### בקרות נגן
**מיקום:** מרכז הנגן
```python
player_controls = {
    "play_pause_button": "⏯️",
    "stop_button": "⏹️",
    "progress_bar": "slider אינטראקטיבי",
    "volume_slider": "בקרת עוצמה",
    "time_display": "1:24 / 3:33"
}
```

#### אזור כתוביות
**מיקום:** חלק תחתון של הנגן
**תכונות:**
- הדגשת השורה הפעילה
- preview של השורה הבאה
- גלילה אוטומטית
- פונט גדול וברור

```python
lyrics_display = {
    "current_line": {
        "text": "Never gonna give you up",
        "style": "bold, highlighted, large"
    },
    "next_line": {
        "text": "Never gonna let you down",
        "style": "gray, smaller"
    },
    "previous_lines": "visible but dimmed",
    "scroll_behavior": "auto-scroll to current"
}
```

## עיבוד נתונים פנימי

### פרסור קובץ LRC
**פונקציה:** `parse_lrc_file(lrc_content)`

**מבנה נתונים פנימי:**
```python
lyrics_data = [
    {
        "timestamp": 0.5,           # שניות מההתחלה
        "end_time": 4.15,          # סוף השורה
        "text": "We're no strangers to love",
        "duration": 3.65,          # משך השורה
        "words": [                 # רמת מילה (אופציונלי)
            {"word": "We're", "start": 0.5, "end": 0.8},
            {"word": "no", "start": 0.9, "end": 1.1}
        ]
    }
]
```

### סנכרון כתוביות
**פונקציה:** `sync_lyrics(current_time, lyrics_data)`

**לוגיקת סנכרון:**
```python
def find_current_line(current_time, lyrics):
    for i, line in enumerate(lyrics):
        if line['timestamp'] <= current_time < line.get('end_time', line['timestamp'] + 4):
            return {
                'current_index': i,
                'current_line': line,
                'next_line': lyrics[i+1] if i+1 < len(lyrics) else None,
                'progress': (current_time - line['timestamp']) / line['duration']
            }
    return None
```

### ניהול קבצי אודיו
**טעינה:** Streamlit Audio Component
**פורמט נתמך:** MP3, WAV
**תכונות:**
- הפעלה/השהיה
- דילוג לזמן מסוים
- בקרת עוצמה
- הצגת progress

```python
audio_config = {
    "autoplay": False,
    "loop": False,
    "controls": True,
    "format": "audio/mpeg",
    "sample_rate": 44100
}
```

## ניהול מצב (Session State)

### מצבי אפליקציה
```python
session_state = {
    # מצב כללי
    "current_page": "search",  # search, library, player
    "user_id": "anonymous",

    # חיפוש
    "search_query": "",
    "search_results": [],
    "loading_search": False,

    # הורדות
    "downloading_songs": {"dQw4w9WgXcQ": "processing"},
    "download_progress": {},

    # נגן
    "current_song": None,
    "is_playing": False,
    "current_time": 0.0,
    "volume": 0.8,
    "lyrics_data": [],
    "audio_file": None
}
```

### ניהול שגיאות ממשק משתמש
```python
ui_error_handling = {
    "network_error": "שגיאת רשת - נסה שוב",
    "song_not_ready": "השיר עדיין בעיבוד",
    "download_failed": "ההורדה נכשלה - נסה שיר אחר",
    "audio_load_error": "שגיאה בטעינת השמע",
    "lrc_parse_error": "שגיאה בטעינת הכתוביות"
}
```

## הגדרות תצוגה וחוויית משתמש

### רספונסיביות
- **מסכי מחשב:** פריסה בשלושה עמודים
- **מסכי טאבלט:** פריסה בשני עמודים
- **מסכי מובייל:** פריסה בעמודה אחת

### נגישות (Accessibility)
- תמיכה בקורא מסך
- ניגוד צבעים גבוה
- בקרות מקלדת
- גופן ברור וגדול

### אנימציות
- מעברים חלקים בין דפים
- הנפשת progress bars
- fade-in/fade-out לכתוביות
- hover effects על כפתורים