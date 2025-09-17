# Streamlit Client - משימות והסבר

## תפקיד הסרוביס
מספק ממשק משתמש מלא לחיפוש, הורדה והפעלת קריוקי, כולל נגן מתקדם עם סנכרון כתוביות.

## תזרים עבודה מפורט (Workflow)

### 1. חיפוש והצגת שירים
1. **קבלת שאילתת חיפוש** מהמשתמש בטופס חיפוש
2. **שליחת בקשה** ל-API Server דרך `POST /search`
3. **קבלת תוצאות** ועיבוד לפורמט תצוגה
4. **הצגת גריד** של כרטיסי שירים עם thumbnails וכפתורי הורדה
5. **ניהול מצבי loading** ושגיאות רשת

### 2. הורדה ומעקב אחר התקדמות
1. **קבלת לחיצה** על כפתור "הורד" משיר נבחר
2. **שליחת בקשת הורדה** ל-API Server דרך `POST /download`
3. **התחלת מעקב** אחר התקדמות העיבוד
4. **Polling תקופתי** (כל 5 שניות) על `GET /songs/{video_id}/status`
5. **עדכון UI** עם progress bar ושלבי העיבוד
6. **הצגת הודעות** למשתמש על סטטוס ושגיאות

### 3. ניהול ספריית שירים
1. **טעינת רשימת שירים** מוכנים דרך `GET /songs`
2. **סינון והצגה** של שירים שעברו עיבוד מלא
3. **מיון לפי** תאריך יצירה או שם
4. **חיפוש פנימי** בספרייה הקיימת
5. **הצגת מטאדאטה** ותמונות של השירים

### 4. נגן קריוקי מתקדם
1. **הורדת קבצי השיר** דרך `GET /songs/{video_id}/download`
2. **חילוץ קבצים** מהארכיון ZIP:
   - `vocals_removed.wav` - קובץ השמע ללא ווקאל
   - `lyrics.lrc` - קובץ הכתוביות עם timestamps
3. **פרסור קובץ LRC** למבנה נתונים פנימי
4. **טעינת קובץ השמע** לרכיב האודיו של Streamlit
5. **הפעלת לולאת סנכרון** לכתוביות עם עדכון כל 100ms
6. **ניהול בקרות נגן** (play/pause/seek/volume)

### 5. סנכרון כתוביות בזמן אמת
1. **מעקב אחר זמן נוכחי** בהשמעת האודיו
2. **זיהוי השורה הפעילה** בהתאם לטיימסטמפ
3. **הדגשת השורה הנוכחית** ועמעום השורות הקודמות
4. **הצגת תצוגה מקדימה** של השורה הבאה
5. **גלילה אוטומטית** לשמירה על השורה הפעילה במרכז
6. **טיפול במעברים** בין שורות וריווחים

## תקשורת עם שירותים אחרים

### עם API Server (HTTP)
- **שולח:** בקשות חיפוש (`POST /search`)
- **שולח:** בקשות הורדה (`POST /download`)
- **מבקש:** רשימת שירים (`GET /songs`)
- **מבקש:** סטטוס שירים (`GET /songs/{video_id}/status`)
- **מוריד:** קבצי קריוקי (`GET /songs/{video_id}/download`)

### עם דפדפן המשתמש
- **מציג:** ממשק משתמש אינטראקטיבי
- **מקבל:** קלט משתמש (חיפושים, לחיצות, בקרות נגן)
- **מנגן:** קבצי אודיו WAV
- **מציג:** כתוביות מסונכרנות בזמן אמת

### עם מערכת הקבצים המקומית (זמני)
- **שומר:** קבצי ZIP שהורדו זמנית
- **חולץ:** קבצי אודיו וכתוביות מהארכיון
- **מנהל:** מטמון קבצים למהירות גישה

## רשימת משימות פיתוח

### Phase 1: תשתית Streamlit בסיסית
- [ ] הקמת פרויקט Streamlit עם מבנה דפים מודולרי
- [ ] יצירת navigation bar לניווט בין דפים
- [ ] הגדרת session state לניהול מצב אפליקציה
- [ ] עיצוב תבנית בסיסית עם CSS מותאם
- [ ] הגדרת הגדרות אפליקציה ומשתני סביבה

### Phase 2: עמוד חיפוש ותוצאות
- [ ] יצירת טופס חיפוש עם validation
- [ ] יישום client ל-API Server לבקשות חיפוש
- [ ] עיצוב גריד תוצאות עם כרטיסי שירים
- [ ] הוספת טעינה אסינכרונית ו-loading states
- [ ] ניהול שגיאות רשת והצגת הודעות למשתמש

### Phase 3: מערכת הורדות ומעקב
- [ ] יישום לוגיקת הורדת שירים
- [ ] מערכת polling לבדיקת סטטוס התקדמות
- [ ] עיצוב progress bar עם שלבי עיבוד
- [ ] ניהול concurrent downloads ומצבי שגיאה
- [ ] notifications למשתמש על השלמת עיבוד

### Phase 4: ספריית שירים
- [ ] עמוד ספרייה עם רשימת שירים מוכנים
- [ ] מערכת חיפוש וסינון פנימית
- [ ] מיון לפי תאריכים, שמות, ואמנים
- [ ] תצוגת metadata מפורטת לכל שיר
- [ ] ניהול מועדפים ופלייליסטים (אופציונלי)

### Phase 5: נגן קריוקי בסיסי
- [ ] הורדה וחילוץ קבצי ZIP
- [ ] רכיב נגן אודיו עם בקרות בסיסיות
- [ ] טעינה והצגה של מטאדאטה השיר
- [ ] ניהול מצבי הפעלה (play/pause/stop)
- [ ] בקרת עוצמה ו-seek bar

### Phase 6: מערכת כתוביות מתקדמת
- [ ] parser לקבצי LRC עם support למטאדאטה
- [ ] אלגוריתם סנכרון כתוביות עם זמן שמע
- [ ] עיצוב אזור כתוביות עם הדגשות
- [ ] גלילה אוטומטית ומעקב שורה פעילה
- [ ] תמיכה בכתוביות רב-שפתיות (עתידי)

### Phase 7: UX ונגישות
- [ ] responsive design למכשירים שונים
- [ ] תמיכה בקיצורי מקלדת לנגן
- [ ] הוספת אנימציות ומעברים חלקים
- [ ] נגישות לבעלי מוגבלויות (ARIA, contrast)
- [ ] dark/light mode toggle

### Phase 8: ביצועים ואופטימיזציה
- [ ] lazy loading לתמונות ותוכן כבד
- [ ] caching של תוצאות חיפוש וסטטוסים
- [ ] אופטימיזציה של מהירות טעינת דפים
- [ ] compression של נתונים בתקשורת
- [ ] ניהול זיכרון ומטמון קבצים

### Phase 9: שגיאות ואמינות
- [ ] error boundaries מקיף לכל הרכיבים
- [ ] retry logic לבקשות רשת כושלות
- [ ] fallback UI למצבי שגיאה
- [ ] validation מקיף של קלט משתמש
- [ ] recovery אוטומטי ממצבי כשל

### Phase 10: תיעוד ובדיקות
- [ ] דוקומנטציה למשתמש קצה
- [ ] unit tests לפונקציות קריטיות
- [ ] integration tests עם API Server
- [ ] user acceptance testing עם משתמשים
- [ ] deployment guide ו-setup instructions

## דרישות טכניות

### תלויות עיקריות
- **streamlit**: מסגרת הממשק
- **requests**: בקשות HTTP ל-API Server
- **pandas**: ניהול נתונים וטבלאות
- **streamlit-audio**: רכיב אודיו מתקדם
- **zipfile**: חילוץ קבצי ZIP
- **datetime**: ניהול זמנים ותאריכים

### משתני סביבה נדרשים
```env
# API Server
API_SERVER_HOST=localhost
API_SERVER_PORT=8000
API_SERVER_BASE_URL=http://localhost:8000

# UI Configuration
APP_TITLE=Karaoke System
APP_ICON=🎤
PAGE_CONFIG_LAYOUT=wide
THEME=auto

# Audio Settings
AUDIO_SAMPLE_RATE=44100
AUDIO_BUFFER_SIZE=1024
LYRICS_SYNC_INTERVAL_MS=100

# Caching
CACHE_TTL_SECONDS=300
MAX_CACHE_SIZE_MB=100
TEMP_FILES_DIR=/tmp/karaoke

# Performance
MAX_CONCURRENT_DOWNLOADS=3
POLLING_INTERVAL_SECONDS=5
REQUEST_TIMEOUT_SECONDS=30
```

### מבנה קבצים מומלץ
```
streamlit-client/
├── app/
│   ├── main.py                    # נקודת כניסה ראשית
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 1_🔍_Search.py         # עמוד חיפוש
│   │   ├── 2_📚_Library.py        # ספריית שירים
│   │   └── 3_🎤_Player.py         # נגן קריוקי
│   ├── components/
│   │   ├── __init__.py
│   │   ├── search_form.py         # טופס חיפוש
│   │   ├── song_card.py           # כרטיס שיר
│   │   ├── progress_tracker.py    # מעקב התקדמות
│   │   ├── player_controls.py     # בקרות נגן
│   │   ├── lyrics_display.py      # תצוגת כתוביות
│   │   └── navigation.py          # ניווט
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py          # client ל-API Server
│   │   ├── audio_player.py        # לוגיקת נגן אודיו
│   │   ├── lrc_parser.py          # פרסור LRC
│   │   ├── file_manager.py        # ניהול קבצים
│   │   └── lyrics_sync.py         # סנכרון כתוביות
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── session_state.py       # ניהול מצב
│   │   ├── ui_helpers.py          # פונקציות עזר UI
│   │   ├── validators.py          # ולידציות
│   │   └── formatters.py          # פורמט נתונים
│   ├── styles/
│   │   ├── main.css               # CSS ראשי
│   │   ├── player.css             # עיצוב נגן
│   │   └── components.css         # עיצוב רכיבים
│   └── config/
│       ├── __init__.py
│       ├── settings.py            # הגדרות אפליקציה
│       └── constants.py           # קבועים
├── assets/                        # תמונות ואייקונים
├── tests/
│   ├── test_components.py
│   ├── test_services.py
│   └── test_ui_flow.py
└── requirements.txt
```

### מבנה Session State
```python
if 'session_state' not in st.session_state:
    st.session_state.update({
        # Navigation
        'current_page': 'search',
        'page_history': [],

        # Search
        'last_search_query': '',
        'search_results': [],
        'search_loading': False,

        # Downloads
        'downloads_tracking': {},  # {video_id: status}
        'download_progress': {},   # {video_id: progress_data}

        # Library
        'library_songs': [],
        'library_loaded': False,
        'library_filter': '',

        # Player
        'current_song': None,
        'player_state': 'stopped',  # stopped/playing/paused
        'current_time': 0.0,
        'total_duration': 0.0,
        'volume': 0.8,
        'lyrics_data': [],
        'current_lyrics_index': -1,

        # UI State
        'show_notifications': True,
        'theme': 'auto',
        'language': 'he'
    })
```

### אינטגרציה עם Streamlit Audio
```python
# דוגמה לרכיב אודיו מותאם
def create_audio_player(audio_file_path):
    audio_component = st_audio(
        audio_file_path,
        format='audio/wav',
        start_time=0,
        sample_rate=44100,
        key=f"audio_player_{st.session_state.current_song['video_id']}"
    )
    return audio_component

# מעקב אחר זמן נוכחי
def sync_lyrics_with_audio():
    current_time = get_audio_current_time()
    active_line = find_active_lyrics_line(current_time)
    update_lyrics_display(active_line)
```