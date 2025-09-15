# Transcription Service - רשימת משימות

## 🎯 תפקיד הסרוויס
תמלול אוטומטי של שירים ויצירת קבצי LRC עם סנכרון זמנים לקריוקי

---

## 📋 משימות פיתוח

### 1. הכנת סביבת הפיתוח
- [ ] יצירת תיקיית `services/transcription-service/`
- [ ] הכנת `Dockerfile` לסרוויס (עם Python ו-speech recognition libraries)
- [ ] יצירת `requirements.txt` עם STT ו-audio processing dependencies
- [ ] הגדרת משתני סביבה (Kafka, Elasticsearch, AI API keys)

### 2. בחירת מנוע Speech-to-Text

#### אפשרויות ליישום:

**Option A: OpenAI Whisper (מומלץ)**
- [ ] התקנת Whisper מ-OpenAI
- [ ] מודלים מקומיים (offline)
- [ ] תמיכה מעולה בשפות שונות
- [ ] דיוק גבוה במוזיקה ושירה

**Option B: Google Speech-to-Text**
- [ ] Google Cloud Speech API
- [ ] דורש חיבור לאינטרנט
- [ ] מעולה לדיבור פחות למוזיקה

**Option C: Azure Speech Services**
- [ ] Microsoft Cognitive Services
- [ ] תמיכה טובה בזמנים
- [ ] דורש API key

**המלצה: Whisper לlocal processing + Google כbackup**

### 3. Core Transcription Engine

#### מודול תמלול בסיסי
- [ ] יצירת `app/services/speech_to_text.py`
- [ ] מימוש `transcribe_audio(audio_path: str) -> TranscriptionResult`:

**עם Whisper:**
```python
def transcribe_with_whisper(audio_path):
    import whisper

    # Load model (once per service)
    model = whisper.load_model("base")  # tiny/base/small/medium/large

    # Transcribe with timestamps
    result = model.transcribe(
        audio_path,
        task="transcribe",
        language="auto-detect",  # or specific language
        word_timestamps=True,
        temperature=0.0  # deterministic
    )

    return {
        "segments": result["segments"],
        "language": result["language"],
        "confidence": calculate_confidence(result),
        "duration": result.get("duration", 0)
    }
```

#### עיבוד טקסט ושיפור
- [ ] יצירת `app/services/text_processor.py`
- [ ] ניקוי טקסט מרעשים ו-artifacts
- [ ] זיהוי וסינון חזרות (припевов)
- [ ] תיקון שגיאות איות נפוצות במילים של שירים
- [ ] שיפור punctuation וcapitalization

### 4. יצירת קבצי LRC

#### מודול LRC Generator
- [ ] יצירת `app/services/lrc_generator.py`
- [ ] מימוש `create_lrc_file(transcription_result, output_path) -> str`:

```python
def create_lrc_file(segments, metadata, output_path):
    lrc_content = []

    # Add metadata headers
    lrc_content.append(f"[ar:{metadata.get('artist', '')}]")
    lrc_content.append(f"[ti:{metadata.get('title', '')}]")
    lrc_content.append(f"[al:{metadata.get('album', '')}]")
    lrc_content.append(f"[by:Karaoke AI System]")
    lrc_content.append("")

    # Add timed lyrics
    for segment in segments:
        start_time = format_lrc_timestamp(segment["start"])
        text = clean_text(segment["text"])
        lrc_content.append(f"[{start_time}]{text}")

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lrc_content))

    return output_path
```

#### Timestamp Formatting
- [ ] מימוש `format_lrc_timestamp(seconds) -> str`:
```python
def format_lrc_timestamp(seconds):
    """Convert seconds to LRC format [mm:ss.xx]"""
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"
```

#### איכות וסנכרון
- [ ] בדיקת overlap בין segments
- [ ] מינימום/מקסימום אורך למשפט
- [ ] Gap detection וטיפול ברווחים
- [ ] חלוקה חכמה של משפטים ארוכים

### 5. אינטגרציה עם Kafka

#### Consumer לבקשות תמלול
- [ ] יצירת `app/consumers/transcription_consumer.py`
- [ ] האזנה לטופיק `transcription.process.requested`
- [ ] עיבוד הודעות בפורמט:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "transcribe",
  "metadata": {
    "title": "Never Gonna Give You Up",
    "artist": "Rick Astley"
  }
}
```

#### Producer לדיווח תוצאות
- [ ] יצירת `app/services/kafka_producer.py`
- [ ] שליחת הודעת סיום לטופיק `transcription.done`:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "transcription_done",
  "lyrics_path": "/shared/audio/dQw4w9WgXcQ/lyrics.lrc",
  "language": "en",
  "confidence": 0.92,
  "word_count": 156,
  "processing_time": 32.1,
  "segments_count": 24
}
```

### 6. אינטגרציה עם Elasticsearch
- [ ] יצירת `app/services/elasticsearch_updater.py`
- [ ] עדכון מסמך השיר לאחר תמלול מוצלח:
```python
def update_song_document(video_id, lyrics_path, transcription_metadata):
    doc_update = {
        "file_paths.lyrics": lyrics_path,
        "updated_at": datetime.utcnow().isoformat(),
        "transcription_metadata": {
            "language": transcription_metadata["language"],
            "confidence": transcription_metadata["confidence"],
            "word_count": transcription_metadata["word_count"],
            "processing_time": transcription_metadata["processing_time"]
        },
        "search_text": extract_searchable_text(lyrics_path)  # for better search
    }
    es_client.update(index="songs", id=video_id, body={"doc": doc_update})
```

### 7. עיבוד שפות ואופטימיזציה

#### רב-לשונית
- [ ] זיהוי אוטומטי של שפה
- [ ] תמיכה בעברית, אנגלית, וכו'
- [ ] מיפוי שגיאות נפוצות לכל שפה
- [ ] Character encoding נכון (UTF-8)

#### אופטימיזציה למוזיקה
- [ ] Pre-processing של audio (noise reduction)
- [ ] זיהוי רקעים מוזיקליים חזקים
- [ ] שיפור דיוק במקרים של distortion
- [ ] Filter לtoo short/too long segments

### 8. ניהול קבצים וביצועים

#### File Management
- [ ] יצירת `app/utils/file_manager.py`
- [ ] ניקוי קבצי audio זמניים
- [ ] בדיקת תקינות קובץ LRC נוצר
- [ ] גיבוי בcloud (אופציונלי)

#### Memory & Performance
- [ ] עיבוד קבצים ארוכים בchunks
- [ ] מימון זיכרון למודלי Whisper
- [ ] Batch processing של מספר קבצים
- [ ] הגבלת מספר עיבודים מקבילים

### 9. טיפול בשגיאות

#### Error Handling
- [ ] טיפול בשגיאות תמלול:
  - קובץ אודיו פגום/לא נתמך
  - שפה לא מזוהה
  - רעש רב מדי (איכות נמוכה)
  - timeout בעיבוד
- [ ] Retry mechanism עם פרמטרים שונים
- [ ] Fallback למודלים אחרים

#### Quality Control
- [ ] בדיקת איכות תמלול:
```python
def validate_transcription_quality(result):
    if result["confidence"] < 0.3:
        raise LowConfidenceError("Transcription confidence too low")

    if len(result["segments"]) < 5:
        raise InsufficientContentError("Too few segments detected")

    return True
```

### 10. ממשק וחיבורים
- [ ] יצירת `app/main.py` עם entry point
- [ ] הפעלת Kafka consumer
- [ ] בדיקות חיבור לשירותים
- [ ] Health check endpoints
- [ ] Model loading וwarm-up

### 11. ניטור ולוגים
- [ ] לוגים מפורטים לכל שלב:
  - קבלת בקשה מKafka
  - התחלת תמלול
  - תוצאות איכות ודיוק
  - זמן עיבוד
  - יצירת LRC
  - עדכון Elasticsearch
- [ ] Metrics collection (דיוק ממוצע, זמן עיבוד)

### 12. בדיקות
- [ ] Unit tests עם קטעי אודיו לדוגמא
- [ ] בדיקת איכות LRC הנוצרים
- [ ] Integration tests עם Kafka mock
- [ ] בדיקת דיוק transcription עם golden dataset
- [ ] Load testing עם קבצים ארוכים

---

## 🔧 טכנולוגיות נדרשות

### Speech Recognition
- **openai-whisper** - מנוע תמלול מקומי איכותי
- **speechrecognition** - wrapper למנועי STT שונים
- **pydub** - עיבוד אודיו בסיסי
- **librosa** - ניתוח אודיו מתקדם

### Text Processing
- **nltk** או **spacy** - עיבוד שפה טבעית
- **langdetect** - זיהוי שפה
- **unidecode** - ניקוי characters מיוחדים

### Infrastructure
- **kafka-python** - Kafka integration
- **elasticsearch-py** - Elasticsearch updates

---

## 📦 Dependencies מוערכות

### מינימליסטי (Whisper)
```txt
openai-whisper==20231117
pydub==0.25.1
librosa==0.10.1
kafka-python==2.0.2
elasticsearch==8.11.0
langdetect==1.0.9
python-dotenv==1.0.0
nltk==3.8.1
```

### מקסימלי (כל האפשרויות)
```txt
# Whisper + alternatives
openai-whisper==20231117
SpeechRecognition==3.10.0
google-cloud-speech==2.23.0
azure-cognitiveservices-speech==1.34.0

# Audio processing
pydub==0.25.1
librosa==0.10.1
soundfile==0.12.1
noisereduce==3.0.0

# Text processing
nltk==3.8.1
spacy>=3.7.0
langdetect==1.0.9
unidecode==1.3.7

# Infrastructure
kafka-python==2.0.2
elasticsearch==8.11.0
```

---

## 🚀 הערות חשובות

### Whisper Model Selection
- **tiny**: מהיר (~5 שניות) דיוק בינוני
- **base**: איזון טוב (~15 שניות)
- **small**: איכות טובה (~30 שניות)
- **medium/large**: איכות גבוהה ביותר (~60+ שניות)

### LRC File Format
```lrc
[ar:Rick Astley]
[ti:Never Gonna Give You Up]
[00:00.50]We're no strangers to love
[00:04.15]You know the rules and so do I
[00:08.20]A full commitment's what I'm thinking of
```

### Language Detection
- שפה אוטומטית עם Whisper
- Fallback לאנגלית אם לא מזוהה
- ספציפיקה ידנית אפשרית

### Docker Considerations
```dockerfile
# Install audio libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Download Whisper model during build
RUN python -c "import whisper; whisper.load_model('base')"
```

### Performance Tips
- המודל נטען פעם אחת בהתחלה
- עיבוד parallel של segments
- Cache תוצאות לשירים פופולריים

### Quality Metrics
```python
def calculate_transcription_confidence(result):
    avg_confidence = sum(s.get("confidence", 0) for s in result["segments"]) / len(result["segments"])
    return avg_confidence
```

השירות הזה דורש ידע ב-NLP ו-Speech Processing!