# תזרימי עבודה מלאים (End-to-End Flows) - מערכת קריוקי

## מבוא

מסמך זה מתאר את תזרימי העבודה המלאים של הפעולות המרכזיות במערכת הקריוקי, לפי הארכיטקטורה המחייבת. כל תזרים מפורט שלב אחר שלב עם הדגשת השירות המבצע, הפעולה, והתקשורת בין השירותים.

## עקרונות ארכיטקטורליים מנחים

- **Streamlit Client** מתקשר אך ורק עם **API Server**
- **API Server** פועל כ-Gateway בלבד ומתקשר אך ורק עם **YouTube Service**
- **YouTube Service** הוא האחראי הבלעדי על יצירת מסמכים ב-Elasticsearch ושליחת פקודות ל-Kafka
- **Processing Services** מקבלים פקודות אך ורק מ-Kafka (עם video_id בלבד) ושולפים נתיבי קבצים מ-Elasticsearch
- **Elasticsearch** הוא מקור האמת היחיד לכל המטאדאטה ונתיבי הקבצים

---

## תזרים 1: חיפוש שיר

### שלב 1: בקשת חיפוש מהמשתמש
**Streamlit Client**: שולח בקשת `POST /search` עם שאילתת החיפוש ל-**API Server**.

### שלב 2: העברת בקשה לשירות YouTube
**API Server**: מקבל את הבקשה ומעביר אותה ב-**HTTP** לנקודת הקצה `POST /search` של **YouTube Service**.

### שלב 3: שאילתה ל-YouTube API
**YouTube Service**: שולח שאילתה ל-**YouTube Data API v3** באמצעות **HTTPS** לחיפוש וידאו.

### שלב 4: קבלת תוצאות מ-YouTube
**YouTube Service**: מקבל תוצאות חיפוש מ-**YouTube API** ומעבד אותן (פילטור, עיצוב).

### שלב 5: החזרת תוצאות ל-API Server
**YouTube Service**: מחזיר רשימה של 10 תוצאות חיפוש מעובדות ל-**API Server** באמצעות **HTTP response**.

### שלב 6: החזרת תוצאות למשתמש
**API Server**: מעביר את התוצאות ללא שינוי ל-**Streamlit Client** באמצעות **HTTP response**.

### שלב 7: הצגת תוצאות
**Streamlit Client**: מציג את רשימת השירים למשתמש לבחירה.

---

## תזרים 2: בקשת הורדה והתחלת עיבוד

### שלב 1: בקשת הורדה מהמשתמש
**Streamlit Client**: שולח בקשת `POST /download` עם פרטי השיר הנבחר (video_id, title, channel, duration, thumbnail) ל-**API Server**.

### שלב 2: העברת בקשה לשירות YouTube
**API Server**: מקבל את הבקשה ומעביר אותה ב-**HTTP** לנקודת הקצה `POST /download` של **YouTube Service**.

### שלב 3: תגובה מיידית למשתמש
**YouTube Service**: מחזיר מיידית תגובת `202 Accepted` ל-**API Server**.
**API Server**: מעביר את התגובה ל-**Streamlit Client** (המשתמש יודע שהבקשה התקבלה).

### שלב 4: יצירת מסמך ראשוני ב-Elasticsearch
**YouTube Service** (אסינכרוני): יוצר מסמך ראשוני ב-**Elasticsearch** באמצעות `PUT /songs/_doc/{video_id}` עם:
- פרטי השיר (title, artist, channel, duration, thumbnail)
- `status: "downloading"`
- `file_paths: {}` (ריק)
- timestamps

### שלב 5: הורדת קובץ האודיו
**YouTube Service**: מוריד את קובץ האודיו המקורי באמצעות **YTDLP** ושומר אותו ב-**Shared Storage** בנתיב `/shared/audio/{video_id}/original.mp3`.

### שלב 6: עדכון מסמך עם נתיב הקובץ המקורי
**YouTube Service**: מעדכן את המסמך ב-**Elasticsearch** באמצעות `POST /songs/_update/{video_id}` עם:
- `file_paths.original: "/shared/audio/{video_id}/original.mp3"`
- `status: "processing"`
- מטאדאטה נוספת (גודל קובץ, זמן הורדה, איכות)

### שלב 7: שליחת פקודות עיבוד ל-Kafka
**YouTube Service**: מפרסם **3 הודעות נפרדות** ל-**Kafka** (כל הודעה מכילה **רק video_id**):

#### הודעה 1: אירוע סיום הורדה
- **Topic**: `song.downloaded`
- **תוכן**: `{"video_id": "...", "status": "downloaded", "metadata": {...}}`

#### הודעה 2: פקודת עיבוד אודיו
- **Topic**: `audio.process.requested`
- **תוכן**: `{"video_id": "...", "action": "remove_vocals"}`

#### הודעה 3: פקודת תמלול
- **Topic**: `transcription.process.requested`
- **תוכן**: `{"video_id": "...", "action": "transcribe"}`

### שלב 8: התחלת עיבוד מקבילי (שני תהליכים נפרדים)

#### תהליך A: עיבוד אודיו
**Audio Processing Service**: מאזין ל-**Kafka** topic `audio.process.requested`.
**Audio Processing Service**: מקבל הודעה עם `video_id` בלבד.
**Audio Processing Service**: שולף את נתיב הקובץ המקורי מ-**Elasticsearch** באמצעות `GET /songs/_doc/{video_id}`.
**Audio Processing Service**: קורא את הקובץ המקורי מ-**Shared Storage** לפי הנתיב שנשלף.
**Audio Processing Service**: מבצע הסרת ווקאל (Center Channel Extraction) ושומר את התוצר ב-**Shared Storage** כ-`vocals_removed.mp3`.
**Audio Processing Service**: מעדכן את המסמך ב-**Elasticsearch** עם `file_paths.vocals_removed` ומטאדאטה של העיבוד.
**Audio Processing Service**: מפרסם אירוע סיום ל-**Kafka** topic `audio.vocals_processed` (ללא נתיבי קבצים).

#### תהליך B: תמלול
**Transcription Service**: מאזין ל-**Kafka** topic `transcription.process.requested`.
**Transcription Service**: מקבל הודעה עם `video_id` בלבד.
**Transcription Service**: שולף את נתיב הקובץ המקורי מ-**Elasticsearch** באמצעות `GET /songs/_doc/{video_id}`.
**Transcription Service**: קורא את הקובץ המקורי מ-**Shared Storage** לפי הנתיב שנשלף.
**Transcription Service**: מבצע תמלול באמצעות **Whisper** ויוצר קובץ **LRC** ב-**Shared Storage** כ-`lyrics.lrc`.
**Transcription Service**: מעדכן את המסמך ב-**Elasticsearch** עם `file_paths.lyrics` ומטאדאטה של התמלול.
**Transcription Service**: מפרסם אירוע סיום ל-**Kafka** topic `transcription.done` (ללא נתיבי קבצים).

---

## תזרים 3: בדיקת סטטוס והורדת קובץ מוכן

### שלב 1: בדיקת סטטוס (Polling)
**Streamlit Client**: שולח בקשות `GET /songs/{video_id}/status` ל-**API Server** מדי 5 שניות.

### שלב 2: שליפת מידע מ-Elasticsearch
**API Server**: מבצע `GET /songs/_doc/{video_id}` ב-**Elasticsearch** לשליפת המסמך.

### שלב 3: חישוב התקדמות על בסיס קיום קבצים
**API Server**: בודק את שדה `file_paths` במסמך ומחשב התקדמות:
- `download: true` אם קיים `file_paths.original`
- `audio_processing: true` אם קיים `file_paths.vocals_removed`
- `transcription: true` אם קיים `file_paths.lyrics`
- `files_ready: true` אם קיימים גם `vocals_removed` וגם `lyrics` (ולא ריקים)

### שלב 4: החזרת סטטוס למשתמש
**API Server**: מחזיר ל-**Streamlit Client** את הסטטוס עם אחוזי ההתקדמות.

### שלב 5: זיהוי השלמת עיבוד
**Streamlit Client**: כאשר `files_ready: true`, מציג למשתמש אפשרות להוריד את קבצי הקריוקי.

### שלב 6: בקשת רשימת כל השירים (מעודכן)
**Streamlit Client**: שולח `GET /songs` ל-**API Server** לקבלת רשימת **כל השירים** (מוכנים + בעיבוד + כושלים).

### שלב 7: שאילתה לכל השירים (מעודכן)
**API Server**: מבצע שאילתה ל-**Elasticsearch** `POST /songs/_search` עם שאילתה פשוטה:
```json
{
  "query": {"match_all": {}},
  "sort": [{"created_at": {"order": "desc"}}]
}
```

### שלב 8: חישוב progress לכל שיר ו-החזרת הרשימה המעודכנת
**API Server**:
1. עבור כל שיר מחשב את ה-`progress` object על בסיס `file_paths`
2. מחזיר ל-**Streamlit Client** רשימה מלאה של שירים עם:
   - כל המידע הקיים
   - `progress` object מחושב
   - `files_ready` (לתאימות לאחור)

### שלב 9: בקשת הורדת קבצי קריוקי
**Streamlit Client**: שולח `GET /songs/{video_id}/download` ל-**API Server** לשיר ספציפי.

### שלב 10: שליפת נתיבי קבצים לקריאה
**API Server**: מבצע `GET /songs/_doc/{video_id}` ב-**Elasticsearch** ושולף את הנתיבים:
- `file_paths.vocals_removed`
- `file_paths.lyrics`

### שלב 11: קריאת קבצים מהאחסון
**API Server**: קורא את שני הקבצים מ-**Shared Storage** לפי הנתיבים שנשלפו:
- קריאת הקובץ `vocals_removed.mp3`
- קריאת הקובץ `lyrics.lrc`

### שלב 12: יצירת ארכיון ZIP
**API Server**: יוצר ארכיון ZIP המכיל את שני הקבצים עם שמות סטנדרטיים.

### שלב 13: החזרת קובץ ZIP למשתמש
**API Server**: מחזיר את קובץ ה-ZIP ל-**Streamlit Client** עם `Content-Type: application/zip`.

### שלב 14: נגינה מקומית
**Streamlit Client**:
- חולץ את הקבצים מה-ZIP
- טוען את קובץ ה-LRC ופורס את הזמנים והטקסט
- מפעיל נגן קריוקי עם סנכרון בזמן אמת בין האודיו לכתוביות

---

## סיכום התזרימים

### זרימת התקשורת בין השירותים

```
תזרים 1 (חיפוש):
User → Streamlit → API Server → YouTube Service → YouTube API
                             ← YouTube Service ← API Server ← Streamlit ← User

תזרים 2 (הורדה ועיבוד):
User → Streamlit → API Server → YouTube Service → Elasticsearch (create)
                                               → YTDLP → Shared Storage
                                               → Elasticsearch (update)
                                               → Kafka (3 messages: video_id only)

Audio Service ← Kafka ← YouTube Service
Audio Service → Elasticsearch (get path) → Shared Storage (read)
Audio Service → Shared Storage (write) + Elasticsearch (update) → Kafka (event)

Transcription Service ← Kafka ← YouTube Service
Transcription Service → Elasticsearch (get path) → Shared Storage (read)
Transcription Service → Shared Storage (write) + Elasticsearch (update) → Kafka (event)

תזרים 3 (סטטוס והורדה):
User → Streamlit → API Server → Elasticsearch (status check)
                             → Elasticsearch (get paths) → Shared Storage (read files)
                             → ZIP creation → Streamlit ← User
```

### עקרונות חשובים

1. **Single Source of Truth**: Elasticsearch מכיל את כל המטאדאטה ונתיבי הקבצים
2. **Minimal Kafka Content**: הודעות Kafka מכילות רק `video_id` ומידע בסיסי
3. **Gateway Pattern**: API Server פועל כ-Gateway בלבד ואינו יוצר או מעדכן נתונים
4. **Orchestration Responsibility**: YouTube Service בלבד מתזמן ויוצר תהליכים
5. **File Path Resolution**: Processing Services תמיד שולפים נתיבי קבצים מ-Elasticsearch
6. **Ready Song Definition**: שיר מוכן = קיום `vocals_removed` ו-`lyrics` ב-Elasticsearch

תזרימים אלו מבטיחים עקביות, אמינות ותחזוקתביות של המערכת תוך הבטחת הפרדת אחריות ברורה בין השירותים.