# Audio Processing Service - רשימת משימות

## 🎯 תפקיד הסרוויס
הסרת ווקאל מקבצי שמע ויצירת track אינסטרומנטלי לקריוקי

---

## 📋 משימות פיתוח

### 1. הכנת סביבת הפיתוח
- [ ] יצירת תיקיית `services/audio-processing-service/`
- [ ] הכנת `Dockerfile` לסרוויס (עם Python ו-audio libraries)
- [ ] יצירת `requirements.txt` עם audio processing libraries
- [ ] הגדרת משתני סביבה (Kafka, Elasticsearch configs)

### 2. בחירת טכנולוגיית הסרת ווקאל

#### אפשרויות ליישום:
**Option A: librosa + scipy (Basic)**
- [ ] מימוש Center Channel Extraction
- [ ] פשוט לביצוע אך איכות בינונית

**Option B: spleeter (Advanced)**
- [ ] התקנת Spleeter מ-Deezer
- [ ] מודלים pre-trained לhigh-quality vocal isolation
- [ ] דורש GPU לביצועים טובים

**Option C: demucs (State-of-the-art)**
- [ ] התקנת Facebook Demucs
- [ ] איכות גבוהה ביותר
- [ ] תמיכה ב-CPU ו-GPU

**המלצה: התחלה עם librosa + מעבר ל-demucs**

### 3. Core Audio Processing

#### מודול הסרת ווקאל
- [ ] יצירת `app/services/vocal_remover.py`
- [ ] מימוש `remove_vocals(input_path: str, output_path: str) -> dict`:

**שיטת Center Channel Extraction (מהירה):**
```python
def center_channel_extraction(audio_path, output_path):
    # Load stereo audio
    y, sr = librosa.load(audio_path, sr=None, mono=False)

    # Extract vocals (center channel)
    vocals = y[0] - y[1]  # L-R
    instrumental = y[0] + y[1]  # L+R

    # Save instrumental
    sf.write(output_path, instrumental, sr)

    return {
        "method": "center_channel",
        "quality_score": calculate_quality(instrumental),
        "processing_time": time_taken
    }
```

**שיטת Demucs (איכות גבוהה):**
```python
def demucs_separation(audio_path, output_path):
    # Use pre-trained model
    model = load_demucs_model("htdemucs")
    sources = separate_audio(model, audio_path)

    # sources: drums, bass, other, vocals
    instrumental = sources["drums"] + sources["bass"] + sources["other"]

    sf.write(output_path, instrumental, sr)
    return separation_metrics
```

#### איכות ואופטימיזציה
- [ ] מימוש `calculate_quality_metrics(audio) -> float`:
  - SNR (Signal-to-Noise Ratio)
  - RMS energy comparison
  - Spectral analysis
- [ ] בחירה אוטומטית של שיטה בהתאם לאיכות הקלט
- [ ] Fallback mechanism (demucs → librosa)

### 4. אינטגרציה עם Kafka

#### Consumer לבקשות עיבוד - קלט
**טופיק:** `audio.process.requested`

**פורמט הודעה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "action": "remove_vocals"
}
```

**קלט קובץ:**
- מיקום: `/shared/audio/dQw4w9WgXcQ/original.mp3`
- פורמט: MP3, 44.1kHz, stereo

- [ ] יצירת `app/consumers/audio_consumer.py`
- [ ] האזנה לטופיק `audio.process.requested`
- [ ] עיבוד הודעות ואימות פורמט

#### Producer לדיווח תוצאות - פלט
**פלט קובץ:**
- מיקום: `/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3`
- פורמט: MP3, 44.1kHz, stereo (ללא ווקאל)

**טופיק:** `audio.vocals_processed`

**פורמט הודעה:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed",
  "vocals_removed_path": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
  "processing_time": 45.2,
  "quality_score": 0.85,
  "method_used": "demucs"
}
```

- [ ] יצירת `app/services/kafka_producer.py`
- [ ] שליחת הודעת סיום לטופיק `audio.vocals_processed`

### 5. אינטגרציה עם Elasticsearch - פלט
**עדכון מסמך השיר לאחר עיבוד מוצלח:**
```json
{
  "_id": "dQw4w9WgXcQ",
  "file_paths.vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
  "updated_at": "2025-09-15T10:33:45Z",
  "processing_metadata.audio": {
    "quality_score": 0.85,
    "processing_time": 45.2,
    "method": "demucs"
  }
}
```

- [ ] יצירת `app/services/elasticsearch_updater.py`
- [ ] מימוש פונקציית `update_song_document()`:
```python
def update_song_document(video_id, vocals_removed_path, metadata):
    doc_update = {
        "file_paths.vocals_removed": vocals_removed_path,
        "updated_at": datetime.utcnow().isoformat(),
        "processing_metadata.audio": {
            "quality_score": metadata["quality_score"],
            "processing_time": metadata["processing_time"],
            "method": metadata["method"]
        }
    }
    es_client.update(index="songs", id=video_id, body={"doc": doc_update})
```

### 6. ניהול קבצים וזיכרון

#### File Management
- [ ] יצירת `app/utils/file_manager.py`
- [ ] וידוא שתיקיית היעד קיימת
- [ ] ניקוי קבצים זמניים לאחר עיבוד
- [ ] בדיקת נפח זמין על הדיסק

#### Memory Management
- [ ] עיבוד קבצים גדולים בchunks
- [ ] שחרור זיכרון לאחר כל עיבוד
- [ ] הגבלת מספר עיבודים מקבילים (2-3 מקסימום)

### 7. טיפול בשגיאות

#### Error Handling
- [ ] טיפול בשגיאות עיבוד:
  - קובץ לא נמצא או פגום
  - פורמט שמע לא נתמך
  - אין מספיק זיכרון/דיסק
  - כשל באלגוריתם הסרת הווקאל
- [ ] Retry mechanism עם backoff
- [ ] Fallback למודלים פשותים יותר

#### Error Reporting
- [ ] שליחת שגיאות ל-Kafka:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "failed",
  "error": {
    "code": "AUDIO_PROCESSING_FAILED",
    "message": "Insufficient audio quality for vocal removal",
    "timestamp": "2025-09-15T10:32:00Z"
  }
}
```
- [ ] עדכון Elasticsearch עם שגיאה

### 8. ממשק וחיבורים
- [ ] יצירת `app/main.py` עם entry point
- [ ] הפעלת Kafka consumer
- [ ] בדיקות חיבור לשירותים
- [ ] Health check endpoints

### 9. ניטור ולוגים
- [ ] לוגים מפורטים לכל שלב עיבוד:
  - קבלת בקשה מKafka
  - התחלת עיבוד השמע
  - תוצאות איכות
  - זמן עיבוד
  - עדכון Elasticsearch
- [ ] Metrics collection (זמן עיבוד ממוצע, אחוז הצלחה)

### 10. בדיקות
- [ ] Unit tests עם קבצי שמע לדוגמא
- [ ] בדיקת איכות output עם מטריקות
- [ ] Integration tests עם Kafka mock
- [ ] Load testing עם קבצים גדולים
- [ ] בדיקת memory leaks

### 11. אופטימיזציה וביצועים
- [ ] GPU acceleration (אם זמין)
- [ ] מימוש multi-threading לעיבוד מקבילי
- [ ] Caching של מודלים ML
- [ ] אופטימיזציה למינימום זמן עיבוד

---

## 🔧 טכנולוגיות נדרשות

### Audio Processing
- **librosa** - Audio analysis and processing
- **soundfile** - Audio I/O
- **scipy** - Signal processing
- **numpy** - Mathematical operations

### Advanced (Optional)
- **demucs** - State-of-the-art source separation
- **spleeter** - Deezer's vocal separation
- **torch** - PyTorch for ML models
- **torchaudio** - Audio processing with PyTorch

### Infrastructure
- **kafka-python** - Kafka integration
- **elasticsearch-py** - Elasticsearch updates

---

## 📦 Dependencies מוערכות

### Basic Version
```txt
librosa==0.10.1
soundfile==0.12.1
scipy==1.11.4
numpy==1.24.4
kafka-python==2.0.2
elasticsearch==8.11.0
python-dotenv==1.0.0
```

### Advanced Version (with ML)
```txt
# Basic + ML libraries
demucs==4.0.1
torch>=2.0.0
torchaudio>=2.0.0
# או
spleeter==2.3.2
tensorflow==2.13.0
```

---

## 🚀 הערות חשובות

### איכות vs. מהירות
- **librosa (center channel)**: מהיר (~10 שניות) אך איכות בינונית
- **demucs**: איכות גבוהה (~60-120 שניות) אך דורש משאבים
- **המלצה**: התחלה עם librosa + שדרוג לdemucs

### Docker Considerations
```dockerfile
# Install audio libraries
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

### GPU Support (אופציונלי)
אם יש GPU זמין:
```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
```

### Resource Management
- הגבלת זיכרון ל-2-4GB per process
- מקסימום 2-3 עיבודים מקביליים
- ניקוי קבצים זמניים

### Quality Metrics
```python
def calculate_quality_score(original, processed):
    # SNR calculation
    snr = calculate_snr(original, processed)
    # Spectral similarity
    spectral_score = spectral_similarity(original, processed)
    return (snr * 0.7) + (spectral_score * 0.3)
```

השירות הזה הוא המורכב ביותר מבחינה טכנית - דרוש ידע באודיו DSP!