# שירות עיבוד אודיו - מפתח B

## המשימה שלך
את/ה אחראי/ת על הפרדת vocals והכנת האודיו לתמלול.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/processor/
2. הפרד vocals מ-accompaniment עם spleeter או demucs
3. זהה BPM ו-beat timing עם librosa
4. נרמל את האודיו
5. שלח ל-transcription_requests

## קבצים שעליך לכתוב:
- src/processor/vocal_separator.py
- src/processor/audio_normalizer.py
- src/processor/beat_detector.py

## המבנה שלך:
```
services/processor/
├── src/
│   ├── app.py              # FastAPI app (כבר קיים)
│   ├── config/
│   │   └── settings.py     # הגדרות לכתוב
│   └── processor/          # קבצים שלך לכתוב
│       ├── vocal_separator.py
│       ├── audio_normalizer.py
│       └── beat_detector.py
├── tests/
├── requirements.txt        # כבר קיים
├── Dockerfile             # כבר קיים
└── README.md              # קובץ זה
```

## הרצה:
```bash
cd services/processor
python src/app.py
```

## Kafka Topics:
- **מאזין ל:** `audio_processing_requests`
- **שולח ל:** `transcription_requests`

## טכנולוגיות בשימוש:
- FastAPI - Web framework
- librosa - עיבוד אודיו
- numpy, scipy - חישובים מתמטיים
- spleeter/demucs - הפרדת vocals
- kafka-python - תקשורת בין שירותים
- pymongo - MongoDB

## זרימת עבודה:
1. קבל הודעת Kafka עם פרטי האודיו
2. טען אודיו מ-MongoDB
3. הפרד vocals מ-accompaniment
4. זהה BPM ו-beat timing
5. נרמל את האודיו
6. שמור תוצאות ב-MongoDB
7. שלח לשירות התמלול

## משימות עיקריות:
### Vocal Separation
- השתמש ב-spleeter או demucs
- הפרד vocals מ-accompaniment
- שמור 2 קבצים נפרדים

### Beat Detection
- זהה BPM עם librosa
- מצא beat timestamps
- שמור מידע ל-metadata

### Audio Normalization
- נרמל עוצמת קול
- וודא איכות אודיו אחידה

**בהצלחה! 🎵**