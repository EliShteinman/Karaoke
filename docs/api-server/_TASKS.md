# API Server - משימות והסבר

## תפקיד הסרוביס
שער כניסה (Gateway) בלבד - מנתב בקשות ומספק תגובות ללקוח ללא עיבוד או יצירת נתונים.

## תזרים עבודה מפורט (Workflow)

### 1. טיפול בחיפוש שירים
1. **קבלת בקשת חיפוש** מ-Streamlit Client דרך `POST /search`
2. **העברת הבקשה במלואה** ל-YouTube Service (HTTP call פנימי)
3. **קבלת תוצאות** מ-YouTube Service (רשימת 10 שירים)
4. **החזרת התוצאות ללקוח** ללא שינוי או עיבוד

### 2. טיפול בבקשת הורדה
1. **קבלת בקשת הורדה** מ-Streamlit Client דרך `POST /download`
2. **העברת הבקשה במלואה** ל-YouTube Service (HTTP call פנימי)
3. **קבלת תגובה** מ-YouTube Service (`202 Accepted`)
4. **החזרת התגובה ללקוח** מיידית ללא עיבוד נוסף

### 3. מתן סטטוס שיר ספציפי
1. **קבלת בקשה** מ-Streamlit Client דרך `GET /songs/{video_id}/status`
2. **שליפת מסמך** מ-Elasticsearch לפי video_id (קריאה בלבד)
3. **שליפת אובייקט הסטטוס המפורט** מהמסמך:
   - `status.overall` - סטטוס כללי
   - `status.download` - מצב ההורדה
   - `status.audio_processing` - מצב עיבוד האודיו
   - `status.transcription` - מצב התמלול
4. **חישוב שדה `is_ready`** דינמית:
   - `true` אם כל השלבים במצב "completed"
   - `false` אחרת
5. **החזרת סטטוס מפורט** עם השדה המחושב

### 4. מתן רשימת שירים מוכנים
1. **קבלת בקשה** מ-Streamlit Client דרך `GET /songs`
2. **ביצוע שאילתה ל-Elasticsearch** (קריאה בלבד):
   - חיפוש מסמכים שבהם קיימים השדות `file_paths.vocals_removed` ו-`file_paths.lyrics`
   - וידוא שהשדות אינם ריקים
3. **עיבוד התוצאות** והוספת השדה `files_ready: true`
4. **החזרת רשימה** של שירים מוכנים לנגינה

### 5. הספקת קבצי קריוקי
1. **קבלת בקשה** מ-Streamlit Client דרך `GET /songs/{video_id}/download`
2. **שליפת נתיבי הקבצים** מ-Elasticsearch (קריאה בלבד)
3. **וידוא שהשיר מוכן** - בדיקת קיום שני הקבצים הנדרשים
4. **קריאת קבצים** מה-Shared Storage:
   - `/shared/audio/{video_id}/vocals_removed.mp3`
   - `/shared/audio/{video_id}/lyrics.lrc`
5. **יצירת ארכיון ZIP** במטמון זמני
6. **החזרת קובץ ZIP** ללקוח עם Content-Type מתאים

## תקשורת עם שירותים אחרים

### עם Streamlit Client
- **מקבל:** כל בקשות ה-HTTP מהלקוח
- **שולח:** תגובות JSON, קבצי ZIP, קודי סטטוס HTTP

### עם YouTube Service
- **שולח:** בקשות חיפוש והורדה (HTTP calls פנימיים)
- **מקבל:** תוצאות חיפוש ותגובות הורדה (JSON)

### עם Elasticsearch
- **קורא בלבד:** מסמכי שירים, שליפת סטטוס, חיפוש שירים מוכנים
- **לא כותב:** אינו יוצר או מעדכן מסמכים

### עם Shared Storage
- **קורא בלבד:** קבצי אודיו וכתוביות להספקה ללקוח
- **לא כותב:** אינו יוצר או מעדכן קבצים

### עם Kafka
- **לא מתקשר:** אינו שולח או מקבל הודעות Kafka

## רשימת משימות פיתוח

### Phase 1: תשתית Gateway בסיסית
- [ ] הקמת פרויקט FastAPI עם מבנה תיקיות נכון
- [ ] הגדרת Pydantic models לכל הבקשות והתגובות
- [ ] יצירת HTTP client ל-YouTube Service
- [ ] הגדרת logging ומטרין מערכת

### Phase 2: Endpoints בסיסיים
- [ ] יישום `POST /search` עם proxy ל-YouTube Service
- [ ] יישום `POST /download` עם proxy ל-YouTube Service
- [ ] יישום `GET /songs/{video_id}/status` עם קריאה מ-Elasticsearch
- [ ] יישום `GET /songs` עם שאילתה מתקדמת

### Phase 3: הספקת קבצים
- [ ] יישום `GET /songs/{video_id}/download` עם יצירת ZIP
- [ ] ניהול שגיאות קריאת קבצים
- [ ] אופטימיזציה של העברת קבצים גדולים
- [ ] מטמון זמני לקבצי ZIP

### Phase 4: אינטגרציות
- [ ] הקמת Elasticsearch client (read-only)
- [ ] ניהול שגיאות מתקשורת עם YouTube Service
- [ ] Validation מתקדמת של קלט
- [ ] Rate limiting ו-security headers

### Phase 5: שגיאות ואמינות
- [ ] ניהול שגיאות מקיף לכל endpoint
- [ ] Retry logic לתקשורת עם שירותים חיצוניים
- [ ] Timeout handling ו-circuit breaker patterns
- [ ] Health checks ו-monitoring

### Phase 6: ביצועים ואופטימיזציה
- [ ] הוספת caching לשאילתות נפוצות
- [ ] אופטימיזציה של שאילתות Elasticsearch
- [ ] Compression של תגובות JSON
- [ ] Connection pooling ו-keep-alive

### Phase 7: תיעוד ובדיקות
- [ ] יצירת OpenAPI documentation אוטומטית
- [ ] כתיבת unit tests לכל endpoint
- [ ] integration tests עם YouTube Service
- [ ] הכנת environment configurations

## דרישות טכניות

### תלויות עיקריות
- **FastAPI**: מסגרת ה-web server
- **uvicorn**: ASGI server
- **elasticsearch**: חיבור ל-Elasticsearch (read-only)
- **httpx**: HTTP client ל-YouTube Service
- **pydantic**: ולידציה של נתונים
- **aiofiles**: קריאה אסינכרונית של קבצים

### משתני סביבה נדרשים
```env
# Elasticsearch (Read-Only)
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=songs

# YouTube Service
YOUTUBE_SERVICE_HOST=localhost
YOUTUBE_SERVICE_PORT=8001
YOUTUBE_SERVICE_BASE_URL=http://localhost:8001

# Storage (Read-Only)
SHARED_STORAGE_PATH=/shared/audio

# API
API_PORT=8000
API_HOST=0.0.0.0
```

### מבנה קבצים מומלץ
```
api-server/
├── app/
│   ├── main.py              # נקודת כניסה
│   ├── routes/              # endpoints
│   │   ├── search.py
│   │   ├── download.py
│   │   ├── songs.py
│   │   └── health.py
│   ├── services/            # לוגיקה עסקית
│   │   ├── elasticsearch_service.py  # read-only
│   │   ├── youtube_service.py        # HTTP client
│   │   └── file_service.py           # ZIP creation
│   ├── models/              # Pydantic schemas
│   │   ├── requests.py
│   │   ├── responses.py
│   │   └── internal.py
│   └── config/              # הגדרות
│       ├── settings.py
│       └── dependencies.py
├── tests/
└── requirements.txt
```

## עקרונות ארכיטקטורליים

### Gateway Pattern
- מתפקד כנקודת כניסה יחידה
- מנתב בקשות ללא עיבוד עסקי
- מספק abstraction layer ללקוח

### Read-Only Elasticsearch Access
- רק שאילתות SELECT/GET
- אין יצירה או עדכון של מסמכים
- שימוש ב-connection pool מותאם

### Stateless Design
- אין שמירת מצב בין בקשות
- כל מידע נשלף מ-Elasticsearch
- ניתן להרחבה אופקית

### Error Transparency
- העברת שגיאות מ-YouTube Service ללקוח
- שגיאות Elasticsearch מתורגמות למשתמש
- Graceful degradation במקרה של כשלים