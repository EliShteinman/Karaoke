# מפרט קוביות מיקרו-סרביסים - יישום קריוקי (גרסת MVP)

## 1. API Server
**תפקיד:** נקודת כניסה יחידה, ניתוב בקשות

### API Endpoints:
- `POST /search` - חיפוש שירים ביוטיוב
- `POST /download` - בקשת הורדת שיר נבחר  
- `GET /songs` - רשימת שירים מוכנים
- `GET /songs/{video_id}/status` - סטטוס שיר ספציפי
- `GET /songs/{video_id}/download` - הורדת קובץ קריוקי

### Endpoint: `POST /download`

**פעולות:**
1. מקבל בקשה להורדת שיר מהלקוח (Streamlit).
2. **יוצר מסמך חדש באינדקס `songs` ב-Elasticsearch.** המסמך יכיל את המטא-דאטה שהתקבל (video_id, title, וכו') וסטטוס התחלתי: `"status": "downloading"`.
3. שולח הודעה לטופיק `song.download.requested` ב-Kafka כדי להתחיל את תהליך ההורדה.
4. מחזיר תגובת `202 Accepted` ללקוח.

### Endpoint: `GET /songs`

**לוגיקת חיפוש מעודכנת:**
במקום לחפש שירים עם `status: "ready"`, **השאילתה באלסטיק תהיה חיפוש כל המסמכים שבהם שני השדות `file_paths.vocals_removed` ו-`file_paths.lyrics` קיימים ואינם ריקים.**

דוגמת שאילתה:
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

### קלט/פלט:
- **קלט:** HTTP requests מ-Streamlit
- **פלט:** JSON responses

### תקשורת:
- ✅ **Elasticsearch:** קריאה וכתיבה (חיפוש, סטטוס, מטאדאטה)
- ✅ **Kafka:** שליחת הודעות להורדה
- ❌ **Shared Storage:** לא גש ישיר

---

## 2. YouTube Service
**תפקיד:** קוביה אחת שמטפלת בכל הלוגיקה של יוטיוב

### שתי הפונקציות:

**פונקציה 1: חיפוש**
- קבלת שאילתת חיפוש מה-API Server
- שליחת בקשה ל-YouTube API
- החזרת 10 תוצאות למשתמש

**פונקציה 2: הורדה**
- קבלת video_id נבחר מהמשתמש  
- הורדת השיר עם YTDLP
- שמירה ב-Shared Storage
- שליחת הודעה ל-Kafka שההורדה הושלמה
- **הפעלת השלבים הבאים בתהליך**

### זרימה:
1. API Server → YouTube Service: `{"query": "rick astley"}`
2. YouTube Service → YouTube API → חיפוש
3. YouTube Service → API Server: רשימת 10 תוצאות
4. משתמש בוחר → API Server → YouTube Service: `{"video_id": "dQw4w9WgXcQ"}`
5. YouTube Service → YTDLP → הורדה
6. **YouTube Service מדווח למערכת על סיום ההורדה:**
   - הוא שולח **אירוע (Event)** לטופיק `song.downloaded` המציין שהעבודה הושלמה:
   ```json
   {
     "video_id": "dQw4w9WgXcQ",
     "status": "downloaded",
     "file_path": "/shared/audio/dQw4w9WgXcQ/original.mp3"
   }
   ```
7. **YouTube Service מפעיל את השלבים הבאים בתהליך:**
   - מיד לאחר מכן, הוא שולח שתי **פקודות (Commands)** נפרדות לטופיקים המתאימים:
   - **פקודה 1** לטופיק `audio.process.requested`:
   ```json
   {
     "video_id": "dQw4w9WgXcQ",
     "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3"
   }
   ```
   - **פקודה 2** לטופיק `transcription.process.requested`:
   ```json
   {
     "video_id": "dQw4w9WgXcQ",
     "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3"
   }
   ```

### תקשורת:
- ✅ **YouTube API:** חיפוש שירים
- ✅ **YTDLP:** הורדת וידאו
- ✅ **Shared Storage:** שמירת קובץ MP3
- ✅ **Kafka:** הודעה על השלמת הורדה + הפעלת שלבים הבאים
- ✅ **Elasticsearch:** עדכון מטאדאטה ופרטי השיר

---

## 3. Audio Processing Service
**תפקיד:** הסרת ווקאל מהשיר

### פונקציונליות:
- האזנה ל-Kafka topic: `audio.process.requested`
- קריאת קובץ מקורי
- הסרת ווקאל (Vocal Isolation/Removal)
- שמירת קובץ מעובד
- **עדכון Elasticsearch עם נתיב הקובץ החדש**

### זרימת עבודה מפורטת:
1. קבלת הודעה מקפקא
2. עיבוד הקובץ והסרת ווקאל
3. שמירת הקובץ המעובד
4. **עדכון המסמך המתאים ב-Elasticsearch והוספת הנתיב תחת `file_paths.vocals_removed`**
5. שליחת הודעה לקפקא על השלמת העיבוד

### קלט/פלט:
- **קלט (Kafka):** `{"video_id": "dQw4w9WgXcQ", "original_path": "/shared/audio/.../original.mp3"}`
- **קלט (File):** `/shared/audio/{video_id}/original.mp3`
- **פלט (File):** `/shared/audio/{video_id}/vocals_removed.mp3`
- **פלט (Elasticsearch):** עדכון `file_paths.vocals_removed`
- **פלט (Kafka):** `{"video_id": "dQw4w9WgXcQ", "vocals_removed_path": "...", "status": "vocals_processed"}`

### תקשורת:
- ✅ **Elasticsearch:** עדכון מסמכים (הוספת נתיב קובץ)
- ✅ **Kafka:** Consumer + Producer
- ✅ **Shared Storage:** קריאה וכתיבה

---

## 4. Transcription Service
**תפקיד:** תמלול השיר ויצירת קובץ LRC

### פונקציונליות:
- האזנה ל-Kafka topic: `transcription.process.requested`
- קריאת קובץ מקורי (עם ווקאל)
- Speech-to-Text + Timestamp sync
- יצירת קובץ LRC
- **עדכון Elasticsearch עם נתיב הקובץ החדש**

### זרימת עבודה מפורטת:
1. קבלת הודעה מקפקא
2. תמלול השיר ויצירת timestamps
3. שמירת קובץ LRC
4. **עדכון המסמך המתאים ב-Elasticsearch והוספת הנתיב תחת `file_paths.lyrics`**
5. שליחת הודעה לקפקא על השלמת התמלול

### קלט/פלט:
- **קלט (Kafka):** `{"video_id": "dQw4w9WgXcQ", "original_path": "/shared/audio/.../original.mp3"}`
- **קלט (File):** `/shared/audio/{video_id}/original.mp3`
- **פלט (File):** `/shared/audio/{video_id}/lyrics.lrc`
- **פלט (Elasticsearch):** עדכון `file_paths.lyrics`
- **פלט (Kafka):** `{"video_id": "dQw4w9WgXcQ", "lyrics_path": "...", "status": "transcription_done"}`

### תקשורת:
- ✅ **Elasticsearch:** עדכון מסמכים (הוספת נתיב קובץ)
- ✅ **Kafka:** Consumer + Producer
- ✅ **Shared Storage:** קריאה וכתיבה

---

## 5. Streamlit Client - דרישות פונקציונליות

**תפקיד:** ממשק משתמש לחיפוש, הורדה ונגינת קריוקי

### דרישות חיפוש והורדה:
- ממשק חיפוש שירים (אינטגרציה עם `POST /search`)
- בחירת שיר מרשימת תוצאות (אינטגרציה עם `POST /download`)
- מעקב אחר סטטוס עיבוד השיר (polling על `GET /songs/{video_id}/status`)

### דרישות נגן קריוקי:
1. **טעינת קבצים:**
   - טעינה ופענוח של קובץ שמע (.mp3) מ-`GET /songs/{video_id}/download`
   - טעינה ופרסור של קובץ כתוביות (.lrc) 

2. **נגינה וסנכרון:**
   - **נגינת שמע:** בקרות play/pause/stop/seek
   - **סנכרון כתוביות:** הצגת שורות הכתוביות בזמן אמת לפי timestamps מקובץ ה-LRC
   - **הדגשה ויזואלית:** הדגשת השורה הפעילה, preview של השורה הבאה

3. **ממשק משתמש:**
   - הצגת מטא-דאטה: תמונת השיר, שם האמן, כותרת השיר
   - בקרות נגן intuitive עם progress bar
   - אזור הצגת כתוביות עם גלילה אוטומטית

### תקשורת:
- ✅ **API Server:** כל הבקשות דרך REST API
- ❌ **גישה ישירה:** אין גישה ישירה לקפקא, אלסטיק או shared storage

---

## Kafka Topics:

1. `song.download.requested` - בקשות הורדה
2. `song.downloaded` - הושלמה הורדה
3. `audio.process.requested` - בקשות עיבוד אודיו
4. `transcription.process.requested` - בקשות תמלול
5. `audio.vocals_processed` - הושלם עיבוד אודיו
6. `transcription.done` - הושלם תמלול

---

## Elasticsearch Index: `songs`

```json
{
  "_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "artist": "Rick Astley",
  "channel": "RickAstleyVEVO", 
  "duration": 213,
  "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "status": "processing", // downloading | processing | failed (לעולם לא "ready" ב-MVP)
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-09-15T10:35:00Z",
  "file_paths": {
    "original": "/shared/audio/dQw4w9WgXcQ/original.mp3",
    "vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
    "lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc"
  },
  "search_text": "rick astley never gonna give you up rickroll"
}
```

**הערה:** ב-MVP, השדה `status` ישאר על `processing` גם כאשר השיר מוכן. זיהוי שירים מוכנים נעשה על ידי בדיקת קיום שני הקבצים `vocals_removed` ו-`lyrics`.

---

## Shared Storage Structure:

```
/shared/audio/
├── {video_id_1}/
│   ├── original.mp3
│   ├── vocals_removed.mp3  
│   └── lyrics.lrc
├── {video_id_2}/
│   ├── original.mp3
│   └── vocals_removed.mp3    # בתהליך...
└── {video_id_3}/
    └── original.mp3          # הורד זה עתה
```

---

## חלוקת עבודה מוצעת:

1. **Backend Developer #1:** API Server + Elasticsearch setup + לוגיקת "שירים מוכנים"
2. **Backend Developer #2:** YouTube Service (חיפוש + הורדה במקום אחד)
3. **Audio Engineer:** Audio Processing Service + אינטגרציה עם Elasticsearch
4. **AI Developer:** Transcription Service + אינטגרציה עם Elasticsearch
5. **Integration Developer:** Kafka setup ותיאום בין השירותים
6. **Frontend Developer:** Streamlit Client