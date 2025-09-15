# API Server - רשימת משימות

## 🎯 תפקיד הסרוויס
נקודת כניסה יחידה למערכת, ניתוב בקשות HTTP וניהול מטאדאטה

---

## 📋 משימות פיתוח

### 1. הכנת סביבת הפיתוח
- [ ] יצירת תיקיית `services/api-server/`
- [ ] הכנת `Dockerfile` לסרוויס
- [ ] יצירת `requirements.txt` עם FastAPI, Elasticsearch, Kafka dependencies
- [ ] הגדרת משתני סביבה ב-`.env`

### 2. מודלי נתונים (Pydantic)
- [ ] יצירת `app/models/requests.py`:
  - `SearchRequest` - חיפוש שירים
  - `DownloadRequest` - בקשת הורדה
- [ ] יצירת `app/models/responses.py`:
  - `SearchResponse` - תוצאות חיפוש
  - `SongStatusResponse` - סטטוס שיר
  - `SongsListResponse` - רשימת שירים מוכנים

### 3. חיבורים ולקוחות
- [ ] יצירת `shared/clients/elasticsearch_client.py`
- [ ] יצירת `shared/clients/kafka_client.py`
- [ ] יצירת `app/services/elasticsearch_service.py`
- [ ] בדיקת חיבור לשירותים בעת הפעלה

### 4. API Endpoints

#### POST /search
- [ ] יצירת `app/routes/search.py`
- [ ] אימות קלט (Pydantic validation)
- [ ] קריאה ל-YouTube Service
- [ ] החזרת 10 תוצאות מעוצבות

#### POST /download
- [ ] יצירת `app/routes/download.py`
- [ ] אימות שהשיר לא קיים כבר
- [ ] יצירת מסמך חדש ב-Elasticsearch עם `status: "downloading"`
- [ ] שליחת הודעה ל-Kafka topic `song.download.requested`
- [ ] החזרת `202 Accepted` עם video_id

#### GET /songs
- [ ] יצירת `app/routes/songs.py`
- [ ] מימוש שאילתה ל-Elasticsearch:
  ```json
  {
    "query": {
      "bool": {
        "must": [
          {"exists": {"field": "file_paths.vocals_removed"}},
          {"exists": {"field": "file_paths.lyrics"}},
          {"bool": {"must_not": [
            {"term": {"file_paths.vocals_removed": ""}},
            {"term": {"file_paths.lyrics": ""}}
          ]}}
        ]
      }
    }
  }
  ```
- [ ] החזרת רשימה עם `files_ready: true`

#### GET /songs/{video_id}/status
- [ ] קריאת מסמך מ-Elasticsearch
- [ ] בדיקת קיום הקבצים בשדה `file_paths`
- [ ] החזרת אובייקט progress מפורט

#### GET /songs/{video_id}/download
- [ ] אימות שהשיר מוכן (שני הקבצים קיימים)
- [ ] יצירת ZIP עם:
  - `vocals_removed.mp3`
  - `lyrics.lrc`
- [ ] החזרת ZIP כ-streaming response

### 5. ממשק וחיבורים
- [ ] יצירת `app/main.py` עם FastAPI app
- [ ] רישום כל ה-routes
- [ ] הוספת middleware ל-CORS
- [ ] יצירת `app/routes/health.py` עם health checks

### 6. טיפול בשגיאות
- [ ] יצירת exception handlers מותאמים
- [ ] לוגים מפורטים לכל בקשה
- [ ] validation errors בפורמט אחיד
- [ ] timeout handling לבקשות חיצוניות

### 7. אופטימיזציה וביצועים
- [ ] Connection pooling ל-Elasticsearch
- [ ] Cache layer לחיפושים פופולריים (Redis אופציונלי)
- [ ] Rate limiting לבקשות
- [ ] Async/await בכל המקומות המתאימים

### 8. בדיקות
- [ ] Unit tests ל-services
- [ ] Integration tests ל-routes
- [ ] בדיקות E2E עם mock services
- [ ] בדיקת production readiness

---

## 🔧 טכנולוגיות נדרשות
- **FastAPI** - מסגרת Web
- **Pydantic** - Validation וSerialization
- **elasticsearch-py** - לקוח Elasticsearch
- **kafka-python** או **aiokafka** - לקוח Kafka
- **uvicorn** - ASGI server
- **pytest** - בדיקות

---

## 📦 Dependencies מוערכות
```txt
fastapi==0.104.1
pydantic==2.5.0
elasticsearch==8.11.0
kafka-python==2.0.2
uvicorn[standard]==0.24.0
python-multipart==0.0.6
aiofiles==23.2.1
```

---

## 🚀 הערות חשובות

### אסטרטגיה לזיהוי שירים מוכנים
במקום להשתמש ב-`status: "ready"`, השרת בודק קיום שני השדות:
- `file_paths.vocals_removed`
- `file_paths.lyrics`

### ניהול קבצים
הסרוויס **לא גושש ישיר** לקבצים. הוא מסתמך על Elasticsearch למטאדאטה ונתיבים.

### חיבור ל-YouTube Service
עבור חיפוש - קריאה ישירה HTTP
עבור הורדה - שליחה ל-Kafka

### זיכרון ו-Performance
- השתמש ב-async/await בכל מקום
- Connection pooling חובה
- עמידות בזמני תגובה של מקסימום 5 שניות