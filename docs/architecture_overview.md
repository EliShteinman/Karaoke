# מפרט מיקרו-סרביסים - מערכת קריוקי (ארכיטקטורה מחייבת)

## סקירה כוללת של המערכת

מערכת הקריוקי מורכבת מחמישה מיקרו-סרביסים עצמאיים המתקשרים באמצעות Kafka ו-HTTP, עם Elasticsearch לניהול מטאדאטה ו-Shared Storage לקבצים. כל שירות אחראי על תחום פונקציונלי ספציפי ומתקשר עם השירותים האחרים באופן אסינכרוני.

## חלוקת אחריות מפורטת

### 1. API Server - Gateway בלבד
**תפקיד עיקרי:** נקודת כניסה יחידה ומנתב בקשות בלבד

**אחריות מלאה:**
- קבלת כל בקשות HTTP מ-Streamlit Client
- ניתוב בקשות חיפוש ל-YouTube Service דרך HTTP
- ניתוב בקשות הורדה ל-YouTube Service דרך HTTP
- קריאת מידע מ-Elasticsearch לצורכי הצגה (read-only)
- מתן סטטוס התקדמות על בסיס בדיקת קיום קבצים
- הספקת קבצי ZIP מוכנים ללקוחות
- ניהול לוגיקת "שירים מוכנים" על בסיס קיום קבצים ב-Elasticsearch

**לא אחראי על:**
- יצירה או עדכון של מסמכים ב-Elasticsearch
- שליחת הודעות ל-Kafka
- ביצוע הורדות בפועל מיוטיוב
- עיבוד אודיו או הסרת ווקאל
- תמלול השירים
- אחסון קבצי מדיה

### 2. YouTube Service - מומחה יוטיוב ומתזמן ראשי
**תפקיד עיקרי:** ניהול כל הפעילות הקשורה ל-YouTube ותיזמור התהליכים

**אחריות מלאה:**
- חיפוש שירים דרך YouTube Data API
- יצירת המסמך הראשוני ב-Elasticsearch עם מטאדאטה
- הורדת קבצי אודיו באמצעות YTDLP
- שמירת קבצים ב-Shared Storage
- עדכון Elasticsearch עם נתיבי קבצים מקוריים
- שליחת פקודות ראשוניות ל-Kafka לעיבוד והתמלול
- ניהול שגיאות הורדה ותקשורת עם YouTube

**לא אחראי על:**
- עיבוד האודיו שהורד
- תמלול או יצירת כתוביות
- הצגת תוצאות לנגן הקריוקי
- קריאת מידע מ-Elasticsearch (רק כותב/יוצר)

### 3. Audio Processing Service - מומחה עיבוד אודיו
**תפקיד עיקרי:** הסרת ווקאל מקבצי האודיו וייצור גרסה ללא ווקאל

**אחריות מלאה:**
- האזנה לפקודות Kafka (`audio.process.requested`) עם video_id בלבד
- שליפת נתיבי קבצים מ-Elasticsearch לפי video_id
- עיבוד קבצי אודיו מקוריים והסרת ווקאל
- יישום אלגוריתמי Center Channel Extraction
- שמירת קבצי אודיו מעובדים ב-Shared Storage
- עדכון Elasticsearch עם נתיבי קבצים מעובדים
- מדידת איכות העיבוד וחישוב ציונים
- ניהול שגיאות עיבוד ודיווח כשלים

**לא אחראי על:**
- הורדה מיוטיוב או מקורות חיצוניים
- תמלול או יצירת כתוביות
- נגינת האודיו או הצגה למשתמש
- חשיפת API או קבלת בקשות HTTP ישירות

### 4. Transcription Service - מומחה תמלול
**תפקיד עיקרי:** תמלול השירים ויצירת קבצי כתוביות LRC עם סנכרון זמן

**אחריות מלאה:**
- האזנה לפקודות Kafka (`transcription.process.requested`) עם video_id בלבד
- שליפת נתיבי קבצים מ-Elasticsearch לפי video_id
- תמלול קבצי אודיו מקוריים באמצעות Whisper
- יצירת קבצי LRC עם timestamps מדויקים
- סנכרון כתוביות עם מבנה שירה
- שמירת קבצי כתוביות ב-Shared Storage
- עדכון Elasticsearch עם נתיבי קבצי כתוביות
- הערכת איכות התמלול ומדידת אמינות

**לא אחראי על:**
- הורדה או עיבוד של קבצי אודיו
- הסרת ווקאל או עיבוד אודיו
- הצגת הכתוביות בנגן
- חשיפת API או קבלת בקשות HTTP ישירות

### 5. Streamlit Client - ממשק משתמש
**תפקיד עיקרי:** ממשק משתמש מלא לחיפוש, הורדה והפעלת קריוקי

**אחריות מלאה:**
- הצגת ממשק חיפוש ותוצאות למשתמש
- ניהול בקשות הורדה ומעקב התקדמות
- הצגת ספריית שירים מוכנים
- נגן קריוקי עם סנכרון כתוביות בזמן אמת
- ניהול מצב אפליקציה ו-session state
- חוויית משתמש ואינטראקציה
- תקשורת אך ורק עם API Server

**לא אחראי על:**
- עיבוד או אחסון קבצים בשרת
- תקשורת ישירה עם שירותי התשתית
- ביצוע פעולות backend או עיבוד נתונים
- ניהול מטאדאטה מעבר לתצוגה

## מערכות תשתית משותפות

### Elasticsearch - מנוע חיפוש ומטאדאטה
**תפקיד:** ניהול מרכזי של מטאדאטה לכל השירים במערכת

**שירותים שכותבים:**
- **YouTube Service:** יוצר מסמכים חדשים ומעדכן נתיבי קבצים מקוריים
- **Audio Processing Service:** מעדכן נתיבי קבצים מעובדים
- **Transcription Service:** מעדכן נתיבי קבצי כתוביות

**שירותים שקוראים:**
- **API Server:** חיפוש שירים מוכנים וסטטוסים (read-only)
- **Audio Processing Service:** שליפת נתיבי קבצים מקוריים
- **Transcription Service:** שליפת נתיבי קבצים מקוריים

### Kafka - תקשורת אסינכרונית
**תפקיד:** תיזמור תהליכי עיבוד ותקשורת בין שירותים

**Topics ומטרותיהם:**
- `song.downloaded`: אירועי סיום הורדה מ-YouTube Service
- `audio.process.requested`: פקודות עיבוד מ-YouTube Service ל-Audio Service (רק video_id)
- `audio.vocals_processed`: אירועי סיום עיבוד מ-Audio Service
- `transcription.process.requested`: פקודות תמלול מ-YouTube Service ל-Transcription Service (רק video_id)
- `transcription.done`: אירועי סיום תמלול מ-Transcription Service

### Shared Storage - אחסון קבצים
**תפקיד:** אחסון מרכזי לכל קבצי המדיה והתוצרים

**מבנה נתיבים:**
```
/shared/audio/{video_id}/
├── original.wav           # YouTube Service
├── vocals_removed.wav     # Audio Processing Service
├── vocals.wav             # Audio Processing Service
└── lyrics.lrc            # Transcription Service
```

## זרימת תהליך מלאה

### 1. חיפוש שירים
```
User → Streamlit Client → API Server → YouTube Service → YouTube API
                                    ← YouTube Service ← API Server ← Streamlit Client ← User
```

### 2. הורדה ועיבוד שיר
```
User → Streamlit Client → API Server → YouTube Service → יצירת מסמך ב-Elasticsearch
                                                      → הורדה עם YTDLP
                                                      → עדכון Elasticsearch
                                                      → שליחת 3 הודעות Kafka:
                                                        ├── song.downloaded (אירוע)
                                                        ├── audio.process.requested (פקודה עם video_id בלבד)
                                                        └── transcription.process.requested (פקודה עם video_id בלבד)

Audio Processing Service ← Kafka ← YouTube Service
Audio Processing Service → Elasticsearch (שליפת נתיב original)
Audio Processing Service → Shared Storage + Elasticsearch → Kafka (אירוע)

Transcription Service ← Kafka ← YouTube Service
Transcription Service → Elasticsearch (שליפת נתיב original)
Transcription Service → Shared Storage + Elasticsearch → Kafka (אירוע)
```

### 3. נגינה וצריכה
```
User → Streamlit Client → API Server → Elasticsearch (בדיקת מוכנות)
                                    → Shared Storage (קריאת קבצים)
                                    → ZIP Creation
                                    → Streamlit Client (הורדת ZIP)
                                    → Local Player + LRC Parser
```

## עקרונות ארכיטקטורליים מחייבים

### עקרון Single Source of Truth למטאדאטה
- Elasticsearch הוא מקור האמת היחיד לכל המטאדאטה ונתיבי הקבצים
- הודעות Kafka מכילות רק video_id ומידע מינימלי, ללא נתיבי קבצים
- שירותי עיבוד שולפים נתיבי קבצים תמיד מ-Elasticsearch

### עקרון Hierarchy מחמיר
- Streamlit Client מתקשר אך ורק עם API Server
- API Server מתקשר אך ורק עם YouTube Service לצורכי חיפוש והורדה
- שירותי עיבוד (Audio, Transcription) מקבלים פקודות אך ורק מ-Kafka
- שירותי עיבוד אינם חושפים API או נקודות כניסה HTTP

### עקרון האחריות הבלעדית
- YouTube Service בלבד יוצר מסמכים ב-Elasticsearch ושולח פקודות ל-Kafka
- API Server פועל כ-Gateway בלבד ואינו יוצר או מעדכן מטאדאטה
- שירותי עיבוד מעדכנים רק את השדות הספציפיים שלהם ב-Elasticsearch

### עקרון "שיר מוכן" - מנגנון סטטוסים מפורט
- כל שיר במערכת מכיל אובייקט סטטוס מפורט:
  ```json
  "status": {
      "overall": "processing", // downloading, processing, completed, failed
      "download": "completed",   // pending, in_progress, completed, failed
      "audio_processing": "in_progress", // pending, in_progress, completed, failed
      "transcription": "pending" // pending, in_progress, completed, failed
  }
  ```
- שיר נחשב מוכן כאשר כל שלבי העיבוד הושלמו (`status.overall = "completed"`)
- API Server מחשב שדה `is_ready` דינמית על בסיס השלמת כל השלבים
- השדה `is_ready` אינו נשמר ב-Elasticsearch אלא מחושב מחדש בכל קריאה

### הפרדת אחריות (Separation of Concerns)
- כל שירות מטפל בתחום פונקציונלי יחיד
- אין חפיפה באחריות בין השירותים
- מינימיזציה של תלויות בין שירותים

### תקשורת אסינכרונית
- שימוש ב-Kafka לתהליכים ארוכי טווח
- HTTP רק לבקשות מיידיות (חיפוש, סטטוס) בין Streamlit, API Server ו-YouTube Service
- אי-תלות בזמני תגובה של שירותים אחרים

### עמידות בכשל (Fault Tolerance)
- כל שירות עצמאי ויכול לכשל בנפרד
- שירותי consumer יכולים להתאושש ולעבד הודעות שהוחמצו
- ניהול שגיאות ברמת השירות הבודד

### ניטרול המורכבות
- API Server מסתיר את המורכבות הפנימית מהלקוח
- כל שירות חושף interface מינימלי ומוגדר בבירור
- שירותי התשתית (Kafka, Elasticsearch) מנוהלים מרכזית

## כללי יישום חובה

### תוכן הודעות Kafka
- הודעות לשירותי עיבוד מכילות **רק** video_id ופרמטרים בסיסיים
- **אסור** לכלול נתיבי קבצים (`file_path`, `original_path`, וכו') בהודעות Kafka
- נתיבי קבצים נשלפים תמיד מ-Elasticsearch על ידי השירות המעבד

### דפוסי קריאה וכתיבה ל-Elasticsearch
- **YouTube Service:** כותב ויוצר מסמכים חדשים
- **Audio Processing Service:** קורא נתיבים + מעדכן שדות audio
- **Transcription Service:** קורא נתיבים + מעדכן שדות transcription
- **API Server:** קורא בלבד (read-only)

### התקשורת המותרת
- **Streamlit ↔ API Server:** HTTP בלבד
- **API Server ↔ YouTube Service:** HTTP בלבד
- **YouTube Service ↔ Processing Services:** Kafka בלבד
- **All Services ↔ Elasticsearch:** לפי הרשאות שהוגדרו
- **All Services ↔ Shared Storage:** לפי הצורך