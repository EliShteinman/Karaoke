# מפרט מיקרו-סרביסים - מערכת קריוקי (ארכיטקטורה מחייבת)

## סקירה כוללת של המערכת

מערכת הקריוקי מורכבת מחמישה מיקרו-סרביסים עצמאיים המתקשרים באמצעות Kafka ו-HTTP, עם Elasticsearch לניהול מטאדאטה ו-Shared Storage לקבצים. כל שירות אחראי על תחום פונקציונלי ספציפי ומתקשר עם השירותים האחרים באופן אסינכרוני.

## חלוקת אחריות מפורטת

### 1. API Server - נקודת כניסה יחידה
**תפקיד עיקרי:** מתזמן כללי של המערכת ונקודת כניסה יחידה לכל הבקשות

**אחריות מלאה:**
- קבלת כל בקשות HTTP מ-Streamlit Client
- ניתוב בקשות חיפוש ל-YouTube Service
- יצירת מסמכים חדשים ב-Elasticsearch לשירים חדשים
- שליחת פקודות הורדה ל-Kafka
- מתן סטטוס התקדמות לשירותים חיצוניים
- הספקת קבצי ZIP מוכנים ללקוחות
- ניהול לוגיקת "שירים מוכנים" על בסיס קיום קבצים

**לא אחראי על:**
- ביצוע הורדות בפועל מיוטיוב
- עיבוד אודיו או הסרת ווקאל
- תמלול השירים
- אחסון קבצי מדיה

### 2. YouTube Service - מומחה יוטיוב
**תפקיד עיקרי:** ניהול כל הפעילות הקשורה ל-YouTube ותיזמור השלבים הבאים

**אחריות מלאה:**
- חיפוש שירים דרך YouTube Data API
- הורדת קבצי אודיו באמצעות YTDLP
- שמירת קבצים ב-Shared Storage
- עדכון Elasticsearch עם נתיבי קבצים מקוריים
- הפעלת השלבים הבאים בתהליך (Audio ו-Transcription)
- ניהול שגיאות הורדה ותקשורת עם YouTube

**לא אחראי על:**
- עיבוד האודיו שהורד
- תמלול או יצירת כתוביות
- הצגת תוצאות לנגן הקריוקי
- ניהול מטאדאטה מעבר לקובץ המקורי

### 3. Audio Processing Service - מומחה עיבוד אודיו
**תפקיד עיקרי:** הסרת ווקאל מקבצי האודיו וייצור גרסה ללא ווקאל

**אחריות מלאה:**
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
- ניהול מטאדאטה כללית של השיר

### 4. Transcription Service - מומחה תמלול
**תפקיד עיקרי:** תמלול השירים ויצירת קבצי כתוביות LRC עם סנכרון זמן

**אחריות מלאה:**
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
- ניהול סטטוס כללי של השיר

### 5. Streamlit Client - ממשק משתמש
**תפקיד עיקרי:** ממשק משתמש מלא לחיפוש, הורדה והפעלת קריוקי

**אחריות מלאה:**
- הצגת ממשק חיפוש ותוצאות למשתמש
- ניהול בקשות הורדה ומעקב התקדמות
- הצגת ספריית שירים מוכנים
- נגן קריוקי עם סנכרון כתוביות בזמן אמת
- ניהול מצב אפליקציה ו-session state
- חוויית משתמש ואינטראקציה

**לא אחראי על:**
- עיבוד או אחסון קבצים בשרת
- תקשורת ישירה עם שירותי התשתית
- ביצוע פעולות backend או עיבוד נתונים
- ניהול מטאדאטה מעבר לתצוגה

## מערכות תשתית משותפות

### Elasticsearch - מנוע חיפוש ומטאדאטה
**תפקיד:** ניהול מרכזי של מטאדאטה לכל השירים במערכת

**שירותים שכותבים:**
- **API Server:** יוצר מסמכים חדשים עם סטטוס ראשוני
- **YouTube Service:** מעדכן נתיבי קבצים מקוריים
- **Audio Processing Service:** מעדכן נתיבי קבצים מעובדים
- **Transcription Service:** מעדכן נתיבי קבצי כתוביות

**שירותים שקוראים:**
- **API Server:** חיפוש שירים מוכנים וסטטוסים
- כל השירותים: שליפת מטאדאטה לצורכי עיבוד

### Kafka - תקשורת אסינכרונית
**תפקיד:** תיזמור תהליכי עיבוד ותקשורת בין שירותים

**Topics ומטרותיהם:**
- `song.download.requested`: פקודות הורדה מ-API Server ל-YouTube Service
- `song.downloaded`: אירועי סיום הורדה מ-YouTube Service
- `audio.process.requested`: פקודות עיבוד מ-YouTube Service ל-Audio Service
- `audio.vocals_processed`: אירועי סיום עיבוד מ-Audio Service
- `transcription.process.requested`: פקודות תמלול מ-YouTube Service ל-Transcription Service
- `transcription.done`: אירועי סיום תמלול מ-Transcription Service

### Shared Storage - אחסון קבצים
**תפקיד:** אחסון מרכזי לכל קבצי המדיה והתוצרים

**מבנה נתיבים:**
```
/shared/audio/{video_id}/
├── original.mp3           # YouTube Service
├── vocals_removed.mp3     # Audio Processing Service
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
User → Streamlit Client → API Server → Elasticsearch (יצירת מסמך)
                                    → Kafka (song.download.requested)
                                    → YouTube Service → YTDLP + Elasticsearch
                                    → Kafka (3 הודעות):
                                      ├── song.downloaded (אירוע)
                                      ├── audio.process.requested (פקודה)
                                      └── transcription.process.requested (פקודה)

Audio Processing Service ← Kafka ← YouTube Service
Audio Processing Service → Shared Storage + Elasticsearch → Kafka (אירוע)

Transcription Service ← Kafka ← YouTube Service
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

## עקרונות ארכיטקטורליים

### הפרדת אחריות (Separation of Concerns)
- כל שירות מטפל בתחום פונקציונלי יחיד
- אין חפיפה באחריות בין השירותים
- מינימיזציה של תלויות בין שירותים

### תקשורת אסינכרונית
- שימוש ב-Kafka לתהליכים ארוכי טווח
- HTTP רק לבקשות מיידיות (חיפוש, סטטוס)
- אי-תלות בזמני תגובה של שירותים אחרים

### מרכזיות נתונים
- Elasticsearch כמקור אמת יחיד למטאדאטה
- Shared Storage לכל הקבצים הפיזיים
- אין שכפול נתונים בין שירותים

### עמידות בכשל (Fault Tolerance)
- כל שירות עצמאי ויכול לכשל בנפרד
- שירותי consumer יכולים להתאושש ולעבד הודעות שהוחמצו
- ניהול שגיאות ברמת השירות הבודד

### ניטרול המורכבות
- API Server מסתיר את המורכבות הפנימית מהלקוח
- כל שירות חושף interface מינימלי ומוגדר בבירור
- שירותי התשתית (Kafka, Elasticsearch) מנוהלים מרכזית