# Audio Processing Service - סכמות קלט ופלט

## סקירה כללית
Audio Processing Service אחראי על הסרת הווקאל מקבצי האודיו המקוריים. השירות מאזין להודעות Kafka המכילות **רק video_id**, שולף את נתיב הקובץ המקורי מ-Elasticsearch, מבצע עיבוד אודיו מתקדם, ומעדכן את Elasticsearch עם מיקום הקובץ המעובד.

## קלט (Inputs)

### הודעות Kafka

#### Topic: `audio.process.requested`
**מבנה ההודעה המתקבלת (רק video_id):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "remove_vocals"
}
```

**שדות חובה:**
- `video_id`: מזהה YouTube יחיד (11 תווים)
- `action`: סוג הפעולה המבוקשת

**שדות אסורים:**
- ❌ `original_path` - נתיבי קבצים אסורים ב-Kafka
- ❌ `file_path` - כל נתיב קובץ
- ❌ מטאדאטה נוספת

### קריאות מ-Elasticsearch

#### שליפת נתיב הקובץ המקורי
**פעולה:** `GET /songs/_doc/{video_id}`

**מטרה:** שליפת נתיב הקובץ המקורי לעיבוד

**תגובת Elasticsearch:**
```json
{
  "_source": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "file_paths": {
      "original": "/shared/audio/dQw4w9WgXcQ/original.wav"
    },
    "status": "processing"
  }
}
```

**שדה נדרש:** `file_paths.original` - נתיב הקובץ המקורי

### קבצים ממערכת הקבצים

#### קובץ האודיו המקורי
**נתיב:** נשלף מ-Elasticsearch (`file_paths.original`)
**פורמט צפוי:** WAV, 44.1kHz, stereo
**דוגמה:** `/shared/audio/dQw4w9WgXcQ/original.wav`

**מאפייני הקובץ הנדרשים:**
- קצב דגימה: 44,100 Hz
- ערוצים: 2 (stereo)
- עומק סיביות: 16-bit
- פורמט: WAV או WAV

## פלט (Outputs)

### קבצים למערכת הקבצים

#### קובץ האודיו ללא ווקאל
**נתיב קבוע:** `/shared/audio/{video_id}/vocals_removed.wav`
**פורמט:** WAV, 44.1kHz, stereo (ללא ווקאל)
**דוגמה:** `/shared/audio/dQw4w9WgXcQ/vocals_removed.wav`

**מאפייני קובץ הפלט:**
- קצב דגימה: 44,100 Hz (זהה למקור)
- ערוצים: 2 (stereo)
- עומק סיביות: 16-bit
- איכות: 128kbps WAV
- עיבוד: הסרת ווקאל באמצעות Center Channel Extraction

### עדכונים ל-Elasticsearch

#### עדכון נתיב קובץ מעובד
**פעולה:** `POST /songs/{video_id}/_update`

**מבנה העדכון (Partial Update):**
```json
{
  "doc": {
    "status.audio_processing": "completed",
    "file_paths.vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.wav",
    "updated_at": "2025-09-15T10:33:45Z",
    "processing_metadata.audio": {
      "processing_time": 45.2,
      "quality_score": 0.85,
      "algorithm": "center_channel_extraction",
      "original_size": 3456789,
      "processed_size": 3123456
    }
  }
}
```

### הודעות Kafka

#### Topic: `audio.vocals_processed`
**מבנה ההודעה הנשלחת (רק video_id וסטטוס):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed",
  "processing_time": 45.2,
  "quality_score": 0.85,
  "algorithm_used": "center_channel_extraction",
  "timestamp": "2025-09-15T10:33:45Z"
}
```

**שדות מותרים:**
- `video_id`: מזהה השיר
- `status`: סטטוס סיום העיבוד
- מטרין ביצועים (זמן, איכות)
- `timestamp`: זמן סיום

**שדות אסורים:**
- ❌ `vocals_removed_path` - נתיבי קבצים אסורים ב-Kafka
- ❌ כל נתיב קובץ

## תהליך העבודה המלא

### 1. קבלת הודעה מ-Kafka
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "remove_vocals"
}
```

### 2. שליפת נתיב מ-Elasticsearch
**שאילתה:**
```
GET /songs/_doc/dQw4w9WgXcQ
```

**קבלת נתיב:**
```json
{
  "file_paths": {
    "original": "/shared/audio/dQw4w9WgXcQ/original.wav"
  }
}
```

### 3. עיבוד הקובץ
**קלט:** `/shared/audio/dQw4w9WgXcQ/original.wav`
**עיבוד:** Center Channel Extraction
**פלט:** `/shared/audio/dQw4w9WgXcQ/vocals_removed.wav`

### 4. עדכון Elasticsearch
```json
{
  "doc": {
    "file_paths.vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.wav"
  }
}
```

### 5. דיווח סיום ל-Kafka
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed"
}
```

## פרמטרי עיבוד אודיו

### אלגוריתם הסרת ווקאל
**שיטה:** Center Channel Extraction
**תיאור:** הסרת הערוץ המרכזי על ידי חיסור הערוץ הימני מהשמאלי

**פרמטרים טכניים:**
```python
processing_config = {
    "method": "center_channel_extraction",
    "low_cut_freq": 100,      # Hz - תדר גבול תחתון
    "high_cut_freq": 8000,    # Hz - תדר גבול עליון
    "vocal_reduction": 0.85,  # אחוז הפחתת ווקאל
    "preserve_stereo": True,  # שמירה על ערוץ סטריאו
    "normalization": True     # נורמליזציה של הקובץ
}
```

### מדדי איכות
**Quality Score Calculation:**
```python
quality_metrics = {
    "vocal_suppression": 0.85,    # אחוז הסרת ווקאל
    "instrumental_preservation": 0.88,  # שמירה על כלי נגינה
    "harmonic_distortion": 0.12,  # עיוות הרמוני
    "frequency_response": 0.91,   # תגובת תדר
    "overall_score": 0.85         # ציון כולל
}
```

## שגיאות ואירועי כשל

### Kafka Error Messages

#### שגיאת עיבוד אודיו
**Topic:** `audio.processing.failed`

**מבנה ההודעה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "failed",
  "error": {
    "code": "AUDIO_PROCESSING_FAILED",
    "message": "Failed to process audio file",
    "details": "Unsupported audio format or corrupted file",
    "processing_stage": "vocal_removal",
    "timestamp": "2025-09-15T10:33:00Z",
    "service": "audio_processing_service"
  }
}
```

### קודי שגיאה אפשריים
- `AUDIO_PROCESSING_FAILED`: כשל כללי בעיבוד אודיו
- `FILE_NOT_FOUND`: קובץ המקור לא נמצא (נתיב מ-Elasticsearch שגוי)
- `ELASTICSEARCH_READ_FAILED`: כשל בשליפת נתיב מ-Elasticsearch
- `INVALID_AUDIO_FORMAT`: פורמט אודיו לא נתמך
- `CORRUPTED_AUDIO_FILE`: קובץ אודיו פגום
- `INSUFFICIENT_STORAGE`: אין מקום בדיסק
- `PROCESSING_TIMEOUT`: עיבוד חרג מזמן המתן המותר
- `ELASTICSEARCH_UPDATE_FAILED`: כשל בעדכון Elasticsearch

### עדכון Elasticsearch עם שגיאה
**פעולה:** `POST /songs/{video_id}/_update`

**מבנה העדכון:**
```json
{
  "doc": {
    "status.audio_processing": "failed",
    "status.overall": "failed",
    "error": {
      "code": "AUDIO_PROCESSING_FAILED",
      "message": "Failed to process audio file",
      "stage": "vocal_removal",
      "timestamp": "2025-09-15T10:33:00Z",
      "service": "audio_processing_service"
    },
    "updated_at": "2025-09-15T10:33:00Z"
  }
}
```

### לוגים ומעקב

#### Log Structure
```json
{
  "timestamp": "2025-09-15T10:33:45Z",
  "level": "INFO",
  "service": "audio_processing_service",
  "video_id": "dQw4w9WgXcQ",
  "stage": "vocal_removal",
  "processing_time": 45.2,
  "input_file": "/shared/audio/dQw4w9WgXcQ/original.wav",
  "output_file": "/shared/audio/dQw4w9WgXcQ/vocals_removed.wav",
  "quality_score": 0.85,
  "message": "Audio processing completed successfully"
}
```

## דרישות טכניות

### תלויות תוכנה נדרשות
- **FFmpeg**: עיבוד אודיו בסיסי
- **librosa**: ניתוח אודיו ועיבוד ספקטרלי
- **numpy**: חישובים מתמטיים
- **scipy**: עיבוד אותות דיגיטליים
- **kafka-python**: תקשורת עם Kafka
- **elasticsearch**: עדכון מסמכים

### דרישות חומרה מינימליות
- **זיכרון RAM**: 2GB זמין לעיבוד
- **מעבד**: ליבות מרובות מומלצות
- **אחסון**: 10GB פנויים למטמון

## עקרונות ארכיטקטורליים חשובים

### אי-העברת נתיבים ב-Kafka
- Kafka מכיל **רק** video_id ומידע מינימלי
- נתיבי קבצים נשלפים **תמיד** מ-Elasticsearch
- זה מבטיח Single Source of Truth

### זרימת המידע הנכונה
1. Kafka → video_id בלבד
2. Elasticsearch → שליפת נתיב הקובץ המקורי
3. File System → קריאת קובץ לפי הנתיב
4. Processing → יצירת קובץ מעובד
5. Elasticsearch → עדכון נתיב הקובץ המעובד
6. Kafka → דיווח סיום (ללא נתיבים)