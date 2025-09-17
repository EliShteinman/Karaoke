# Transcription Service - סכמות קלט ופלט

## סקירה כללית
Transcription Service אחראי על תמלול השירים ויצירת קבצי כתוביות LRC עם סנכרון זמן מדויק. השירות מאזין להודעות Kafka המכילות **רק video_id**, שולף את נתיב הקובץ המקורי מ-Elasticsearch, מבצע Speech-to-Text על קבצי האודיו המקוריים, ויוצר קבצי LRC עם timestamps מסונכרנים.

## קלט (Inputs)

### הודעות Kafka

#### Topic: `transcription.process.requested`
**מבנה ההודעה המתקבלת (רק video_id):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "transcribe"
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

**מטרה:** שליפת נתיב הקובץ המקורי לתמלול

**תגובת Elasticsearch:**
```json
{
  "_source": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "artist": "Rick Astley",
    "file_paths": {
      "original": "/shared/audio/dQw4w9WgXcQ/original.mp3"
    },
    "status": "processing"
  }
}
```

**שדה נדרש:** `file_paths.original` - נתיב הקובץ המקורי

### קבצים ממערכת הקבצים

#### קובץ האודיו המקורי
**נתיב:** נשלף מ-Elasticsearch (`file_paths.original`)
**פורמט צפוי:** MP3, 44.1kHz, stereo (עם ווקאל)
**דוגמה:** `/shared/audio/dQw4w9WgXcQ/original.mp3`

**מאפייני הקובץ הנדרשים:**
- קצב דגימה: 16,000-48,000 Hz
- ערוצים: 1 (mono) או 2 (stereo)
- משך: עד 10 דקות למיטוב ביצועים
- שפה: אנגלית (בעיקר)

## פלט (Outputs)

### קבצים למערכת הקבצים

#### קובץ כתוביות LRC
**נתיב קבוע:** `/shared/audio/{video_id}/lyrics.lrc`
**פורמט:** LRC (Lyric File Format)
**דוגמה:** `/shared/audio/dQw4w9WgXcQ/lyrics.lrc`

**מבנה קובץ LRC:**
```lrc
[ar:Rick Astley]
[ti:Never Gonna Give You Up]
[al:Whenever You Need Somebody]
[au:Rick Astley]
[length:03:33]
[by:transcription_service]
[offset:0]

[00:00.50]We're no strangers to love
[00:04.15]You know the rules and so do I
[00:08.20]A full commitment's what I'm thinking of
[00:12.50]You wouldn't get this from any other guy
[00:16.80]I just wanna tell you how I'm feeling
[00:20.90]Gotta make you understand
[00:25.50]Never gonna give you up
[00:27.85]Never gonna let you down
[00:30.20]Never gonna run around and desert you
[00:34.50]Never gonna make you cry
[00:36.85]Never gonna say goodbye
[00:39.20]Never gonna tell a lie and hurt you
```

**פורמט Timestamp:**
- `[mm:ss.xx]` - דקות:שניות.אלפיות השנייה
- דיוק של 0.1 שנייה
- התחלה מ-00:00.00

### עדכונים ל-Elasticsearch

#### עדכון נתיב קובץ כתוביות
**פעולה:** `POST /songs/{video_id}/_update`

**מבנה העדכון (Partial Update):**
```json
{
  "doc": {
    "status.transcription": "completed",
    "status.overall": "completed",
    "file_paths.lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
    "updated_at": "2025-09-15T10:34:12Z",
    "processing_metadata.transcription": {
      "processing_time": 32.1,
      "confidence_score": 0.92,
      "language_detected": "en",
      "word_count": 156,
      "line_count": 32,
      "model_used": "whisper-large-v3"
    }
  }
}
```

### הודעות Kafka

#### Topic: `transcription.done`
**מבנה ההודעה הנשלחת (רק video_id וסטטוס):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "transcription_done",
  "language": "en",
  "confidence": 0.92,
  "word_count": 156,
  "line_count": 32,
  "processing_time": 32.1,
  "model_used": "whisper-large-v3",
  "metadata": {
    "silence_detection": true,
    "background_noise_level": 0.05,
    "vocal_clarity": 0.88,
    "timestamps_accuracy": 0.91
  },
  "timestamp": "2025-09-15T10:34:12Z"
}
```

**שדות מותרים:**
- `video_id`: מזהה השיר
- `status`: סטטוס סיום התמלול
- מטרין ביצועים (זמן, איכות, אמינות)
- `timestamp`: זמן סיום

**שדות אסורים:**
- ❌ `lyrics_path` - נתיבי קבצים אסורים ב-Kafka
- ❌ כל נתיב קובץ

## תהליך העבודה המלא

### 1. קבלת הודעה מ-Kafka
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "transcribe"
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
    "original": "/shared/audio/dQw4w9WgXcQ/original.mp3"
  }
}
```

### 3. תמלול עם Whisper
**קלט:** `/shared/audio/dQw4w9WgXcQ/original.mp3`
**עיבוד:** Speech-to-Text עם Whisper Large v3
**פלט:** קובץ LRC עם timestamps

### 4. שמירת קובץ LRC
**נתיב:** `/shared/audio/dQw4w9WgXcQ/lyrics.lrc`

### 5. עדכון Elasticsearch
```json
{
  "doc": {
    "file_paths.lyrics": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc"
  }
}
```

### 6. דיווח סיום ל-Kafka
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "transcription_done"
}
```

## פרמטרי תמלול

### הגדרות מודל Speech-to-Text
**מודל:** OpenAI Whisper Large v3
**שפה:** Auto-detect (בעיקר אנגלית)

**פרמטרים טכניים:**
```python
transcription_config = {
    "model": "whisper-large-v3",
    "language": "auto",          # זיהוי אוטומטי של שפה
    "task": "transcribe",        # תמלול (לא תרגום)
    "temperature": 0.0,          # דטרמיניסטי
    "beam_size": 5,             # חיפוש קרן
    "best_of": 1,               # מספר ניסיונות
    "word_timestamps": True,     # timestamps ברמת מילה
    "vad_filter": True,         # Voice Activity Detection
    "vad_parameters": {
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "max_speech_duration_s": 30,
        "min_silence_duration_ms": 2000,
        "speech_pad_ms": 400
    }
}
```

### עיבוד פוסט-תמלול
**שיפור כתוביות:**
```python
post_processing = {
    "sentence_segmentation": True,    # חלוקה למשפטים
    "punctuation_restoration": True, # השלמת פיסוק
    "capitalization": True,          # הגדלת אותיות ראשונות
    "profanity_filter": False,       # ללא צנזורה למוזיקה
    "repetition_filter": True,       # הסרת חזרות מיותרות
    "silence_threshold": 2.0,        # רווח מינימלי בין שורות (שניות)
    "max_line_length": 60           # אורך שורה מקסימלי
}
```

### סנכרון זמן מתקדם
**אלגוריתם Timestamp Alignment:**
```python
timing_adjustment = {
    "beat_detection": True,          # זיהוי קצב המוזיקה
    "vocal_onset_detection": True,   # זיהוי התחלות קטעי שירה
    "rhythm_sync": True,             # סנכרון לקצב
    "smooth_transitions": True,      # מעברים חלקים בין שורות
    "early_display": 0.5,           # הצגה מוקדמת (שניות)
    "fade_out_delay": 1.0           # זמן דהייה (שניות)
}
```

## שגיאות ואירועי כשל

### Kafka Error Messages

#### שגיאת תמלול
**Topic:** `transcription.failed`

**מבנה ההודעה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "failed",
  "error": {
    "code": "TRANSCRIPTION_FAILED",
    "message": "Failed to transcribe audio",
    "details": "Audio quality too low or no vocals detected",
    "processing_stage": "speech_to_text",
    "model_used": "whisper-large-v3",
    "confidence_threshold": 0.3,
    "actual_confidence": 0.15,
    "timestamp": "2025-09-15T10:34:00Z",
    "service": "transcription_service"
  }
}
```

### קודי שגיאה אפשריים
- `TRANSCRIPTION_FAILED`: כשל כללי בתמלול
- `FILE_NOT_FOUND`: קובץ המקור לא נמצא (נתיב מ-Elasticsearch שגוי)
- `ELASTICSEARCH_READ_FAILED`: כשל בשליפת נתיב מ-Elasticsearch
- `AUDIO_QUALITY_TOO_LOW`: איכות אודיו ירודה מדי
- `NO_VOCALS_DETECTED`: לא זוהו קטעי שירה
- `LANGUAGE_NOT_SUPPORTED`: שפה לא נתמכת
- `AUDIO_TOO_LONG`: קובץ אודיו ארוך מדי
- `MODEL_LOADING_FAILED`: כשל בטעינת מודל STT
- `INSUFFICIENT_MEMORY`: זיכרון לא מספיק
- `ELASTICSEARCH_UPDATE_FAILED`: כשל בעדכון Elasticsearch

### עדכון Elasticsearch עם שגיאה
**פעולה:** `POST /songs/{video_id}/_update`

**מבנה העדכון:**
```json
{
  "doc": {
    "status.transcription": "failed",
    "status.overall": "failed",
    "error": {
      "code": "TRANSCRIPTION_FAILED",
      "message": "Failed to transcribe audio",
      "stage": "speech_to_text",
      "confidence_achieved": 0.15,
      "confidence_required": 0.3,
      "timestamp": "2025-09-15T10:34:00Z",
      "service": "transcription_service"
    },
    "updated_at": "2025-09-15T10:34:00Z"
  }
}
```

### מדדי איכות

#### ציוני אמינות
```python
quality_metrics = {
    "overall_confidence": 0.92,       # ציון אמינות כללי
    "word_level_confidence": 0.89,    # אמינות ברמת מילה
    "timestamp_accuracy": 0.91,       # דיוק סנכרון זמן
    "language_detection": 0.98,       # זיהוי שפה
    "noise_robustness": 0.85,         # עמידות לרעש
    "vocal_separation": 0.87          # הפרדת ווקאל מכלי נגינה
}
```

### לוגים ומעקב

#### Log Structure
```json
{
  "timestamp": "2025-09-15T10:34:12Z",
  "level": "INFO",
  "service": "transcription_service",
  "video_id": "dQw4w9WgXcQ",
  "stage": "transcription_complete",
  "processing_time": 32.1,
  "input_file": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "output_file": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
  "confidence_score": 0.92,
  "word_count": 156,
  "language": "en",
  "model": "whisper-large-v3",
  "message": "Transcription completed successfully"
}
```

## דרישות טכניות

### תלויות תוכנה נדרשות
- **OpenAI Whisper**: מודל Speech-to-Text
- **ffmpeg**: המרת אודיו ועיבוד
- **torch**: PyTorch לרשת נוירלית
- **librosa**: ניתוח אודיו
- **vad**: Voice Activity Detection
- **kafka-python**: תקשורת עם Kafka
- **elasticsearch**: עדכון מסמכים

### דרישות חומרה מינימליות
- **זיכרון RAM**: 8GB (לWhisper Large)
- **GPU**: מומלץ, לא חובה
- **מעבד**: ליבות מרובות מומלצות
- **אחסון**: 5GB למודלים

## עקרונות ארכיטקטורליים חשובים

### אי-העברת נתיבים ב-Kafka
- Kafka מכיל **רק** video_id ומידע מינימלי
- נתיבי קבצים נשלפים **תמיד** מ-Elasticsearch
- זה מבטיח Single Source of Truth

### זרימת המידע הנכונה
1. Kafka → video_id בלבד
2. Elasticsearch → שליפת נתיב הקובץ המקורי
3. File System → קריאת קובץ לפי הנתיב
4. Processing → יצירת קובץ LRC
5. Elasticsearch → עדכון נתיב הקובץ המעובד
6. Kafka → דיווח סיום (ללא נתיבים)