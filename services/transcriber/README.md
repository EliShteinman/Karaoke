# שירות תמלול עברי - מפתח C

## המשימה שלך
את/ה אחראי/ת על תמלול אודיו לטקסט עברי עם timestamps.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/transcriber/
2. תמלל אודיו עם Whisper או Vosk
3. עבד טקסט עברי עם hebrew-tokenizer
4. צור segments עם timestamps מדויקים
5. שלח ל-lrc_generation_requests

## קבצים שעליך לכתוב:
- src/transcriber/whisper_client.py
- src/transcriber/hebrew_processor.py
- src/transcriber/segment_manager.py

## המבנה שלך:
```
services/transcriber/
├── src/
│   ├── app.py              # FastAPI app (כבר קיים)
│   ├── config/
│   │   └── settings.py     # הגדרות לכתוב
│   └── transcriber/        # קבצים שלך לכתוב
│       ├── whisper_client.py
│       ├── hebrew_processor.py
│       └── segment_manager.py
├── tests/
├── requirements.txt        # כבר קיים
├── Dockerfile             # כבר קיים
└── README.md              # קובץ זה
```

## הרצה:
```bash
cd services/transcriber
python src/app.py
```

## Kafka Topics:
- **מאזין ל:** `transcription_requests`
- **שולח ל:** `lrc_generation_requests`

## טכנולוגיות בשימוש:
- FastAPI - Web framework
- openai-whisper - תמלול אודיו
- vosk - אלטרנטיבה לתמלול
- hebrew-tokenizer - עיבוד טקסט עברי
- elasticsearch - אינדקס תוצאות
- kafka-python - תקשורת בין שירותים
- pymongo - MongoDB

## זרימת עבודה:
1. קבל הודעת Kafka עם פרטי האודיו המעובד
2. טען vocals track מ-MongoDB
3. תמלל עם Whisper (או Vosk)
4. עבד טקסט עברי
5. צור segments עם timestamps
6. שמור ב-MongoDB ו-Elasticsearch
7. שלח לשירות יצירת LRC

## משימות עיקריות:
### Audio Transcription
- השתמש ב-Whisper לתמלול איכותי
- קבל word-level timestamps
- טפל בעברית בצורה מיטבית

### Hebrew Text Processing
- השתמש ב-hebrew-tokenizer
- נקה וסדר טקסט
- תקן שגיאות נפוצות

### Segment Management
- צור TranscriptSegment objects
- וודא timestamps מדויקים
- סדר לפי זמן

## אתגרים מיוחדים:
- תמלול עברית איכותי
- זיהוי מילים מדוברות vs. כתובות
- טיפול בניקוד ובהגיות שונות

**בהצלחה! 🎵**