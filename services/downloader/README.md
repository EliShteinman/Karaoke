# שירות הורדה - מפתח A

## המשימה שלך
את/ה אחראי/ת על הורדת שירים מיוטיוב והמרה לאודיו.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/downloader/
2. הוסף לוגיקה להורדה עם yt-dlp
3. המר לאודיו WAV 16kHz mono עם ffmpeg
4. שמור ב-MongoDB עם הקוד המשותף
5. שלח הודעה ל-Kafka topic: audio_processing_requests

## קבצים שעליך לכתוב:
- src/downloader/youtube_client.py
- src/downloader/audio_converter.py
- src/downloader/metadata_manager.py

## הרצה:
```bash
cd services/downloader
python src/app.py
```

## בדיקה:
```bash
POST http://localhost:8000/download
```

## Kafka Topics:
- **מאזין ל:** `youtube_download_requests`
- **שולח ל:** `audio_processing_requests`

## המבנה שלך:
```
services/downloader/
├── src/
│   ├── app.py              # FastAPI app (כבר קיים)
│   ├── config/
│   │   └── settings.py     # הגדרות (כבר קיים)
│   └── downloader/         # קבצים שלך לכתוב
│       ├── youtube_client.py
│       ├── audio_converter.py
│       └── metadata_manager.py
├── tests/
├── requirements.txt        # כבר קיים
├── Dockerfile             # כבר קיים
└── README.md              # קובץ זה
```

## טכנולוגיות בשימוש:
- FastAPI - Web framework
- yt-dlp - הורדה מיוטיוב
- ffmpeg-python - המרת אודיו
- kafka-python - תקשורת בין שירותים
- pymongo - MongoDB
- elasticsearch - חיפוש ומעקב

## זרימת עבודה:
1. קבל בקשת הורדה (URL + song_id)
2. הורד מיוטיוב עם yt-dlp
3. המר לאודיו WAV 16kHz mono
4. שמור ב-MongoDB GridFS
5. שלח הודעה לשירות עיבוד האודיו

**בהצלחה! 🎵**