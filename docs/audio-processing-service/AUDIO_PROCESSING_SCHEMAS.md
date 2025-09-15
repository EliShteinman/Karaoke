# Audio Processing Service - סכמות קלט ופלט

## סקירה כללית
מסמך זה מכיל את הסכמות המלאות לכל נקודות הקלט והפלט של שירות עיבוד האודיו.

**עיקרון חשוב בנוגע לנתיבי קבצים:**
- נתיב הקובץ המקורי מתקבל **רק דרך הודעת Kafka** (לצרכים פנימיים בין השירותים)
- נתיב הקובץ המעובד נשמר **רק ב-Elasticsearch**
- **אין שליפת נתיבי קבצים מ-Elasticsearch לפני העיבוד** - השירות מסתמך על הנתיב שמועבר ב-Kafka

---

## 1. קלט - הודעת Kafka

### Kafka Consumer
**טופיק:** `audio.process.requested`

**Schema הודעה מתוקנת (רק ID!):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "action": "remove_vocals",
  "timestamp": "2025-09-15T10:32:00Z"
}
```

**Schema Python (Pydantic):**
```python
from pydantic import BaseModel, Field
from typing import Literal

class AudioProcessRequest(BaseModel):
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$', description="YouTube video ID")
    action: Literal["remove_vocals"] = Field(..., description="Type of audio processing to perform")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    class Config:
        schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "action": "remove_vocals",
                "timestamp": "2025-09-15T10:32:00Z"
            }
        }
```

**אימותים נדרשים:**
```python
def validate_audio_request(request: AudioProcessRequest) -> bool:
    # בדיקת קיום הקובץ
    if not os.path.exists(request.original_path):
        raise FileNotFoundError(f"Original file not found: {request.original_path}")

    # בדיקת פורמט קובץ
    if not request.original_path.endswith('.mp3'):
        raise ValueError("Only MP3 files are supported")

    # בדיקת גודל קובץ (מקסימום 100MB)
    file_size = os.path.getsize(request.original_path)
    if file_size > 100 * 1024 * 1024:
        raise ValueError("File too large (max 100MB)")

    return True
```

---

## 2. קלט - קובץ אודיו

### פרמטרי קובץ הקלט
**מיקום:** `/shared/audio/{video_id}/original.mp3`
**פורמט טכני:**
- **Codec:** MP3
- **Sample Rate:** 44.1kHz או 48kHz
- **Channels:** Stereo (2 channels)
- **Bitrate:** 128-320 kbps
- **Duration:** 30 שניות - 2 שעות

**Schema אודיו טכני (Python):**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioFileSpec:
    file_path: str
    sample_rate: int  # Hz
    channels: int     # 1=mono, 2=stereo
    duration: float   # seconds
    bitrate: int      # kbps
    file_size: int    # bytes
    format: str       # 'mp3'

def load_audio_metadata(file_path: str) -> AudioFileSpec:
    """Extract audio file specifications using librosa"""
    import librosa
    import os

    y, sr = librosa.load(file_path, sr=None, mono=False)
    duration = librosa.get_duration(y=y, sr=sr)
    file_size = os.path.getsize(file_path)

    return AudioFileSpec(
        file_path=file_path,
        sample_rate=sr,
        channels=y.shape[0] if len(y.shape) > 1 else 1,
        duration=duration,
        bitrate=int((file_size * 8) / duration / 1000),  # approximate
        file_size=file_size,
        format='mp3'
    )
```

---

## 3. עיבוד - אלגוריתמים

### 3.1 Center Channel Extraction (מהיר)
**פונקציית עיבוד:**
```python
def center_channel_extraction(input_path: str, output_path: str) -> dict:
    """
    הסרת ווקאל באמצעות הפחתת אמצע הערוץ (L-R)
    מהיר אך איכות בינונית
    """
    import librosa
    import soundfile as sf
    import time

    start_time = time.time()

    # טעינת אודיו סטריאו
    y, sr = librosa.load(input_path, sr=None, mono=False)

    if len(y.shape) == 1:
        raise ValueError("Input file must be stereo")

    # הסרת ווקאל: L - R (הפחתת אמצע)
    vocals_removed = y[0] - y[1]

    # נרמול האמפליטודה
    max_amplitude = np.max(np.abs(vocals_removed))
    if max_amplitude > 0:
        vocals_removed = vocals_removed / max_amplitude * 0.95

    # שמירת הקובץ
    sf.write(output_path, vocals_removed, sr)

    processing_time = time.time() - start_time

    return {
        "method": "center_channel_extraction",
        "processing_time": processing_time,
        "quality_score": calculate_quality_score(y, vocals_removed),
        "output_file_size": os.path.getsize(output_path)
    }
```

### 3.2 Demucs Separation (איכות גבוהה)
**פונקציית עיבוד:**
```python
def demucs_separation(input_path: str, output_path: str) -> dict:
    """
    הסרת ווקאל באמצעות Demucs ML model
    איכות גבוהה אך איטי יותר
    """
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    import time

    start_time = time.time()

    # טעינת המודל
    model = get_model('htdemucs')

    # טעינת אודיו
    waveform, sr = torchaudio.load(input_path)

    # הפרדת המקורות
    sources = apply_model(model, waveform.unsqueeze(0))

    # sources shape: [batch, sources, channels, time]
    # sources order: drums, bass, other, vocals
    drums, bass, other, vocals = sources[0]

    # יצירת track אינסטרומנטלי (ללא ווקאל)
    instrumental = drums + bass + other

    # שמירת הקובץ
    torchaudio.save(output_path, instrumental, sr)

    processing_time = time.time() - start_time

    return {
        "method": "demucs",
        "processing_time": processing_time,
        "quality_score": calculate_separation_quality(sources),
        "output_file_size": os.path.getsize(output_path),
        "model_used": "htdemucs"
    }
```

### 3.3 חישוב איכות
```python
def calculate_quality_score(original: np.ndarray, processed: np.ndarray) -> float:
    """
    חישוב ציון איכות לעיבוד האודיו
    Returns: float between 0.0-1.0
    """
    # Signal-to-Noise Ratio
    signal_power = np.mean(processed ** 2)
    noise_power = np.mean((original[0] - processed) ** 2)  # השוואה לערוץ שמאל

    if noise_power == 0:
        snr = float('inf')
    else:
        snr = 10 * np.log10(signal_power / noise_power)

    # Spectral similarity using MFCC
    from librosa.feature import mfcc

    # MFCC המקורי
    mfcc_orig = mfcc(y=original[0], sr=22050, n_mfcc=13)
    # MFCC המעובד
    mfcc_proc = mfcc(y=processed, sr=22050, n_mfcc=13)

    # דמיון ספקטרלי
    spectral_similarity = np.corrcoef(
        mfcc_orig.flatten(),
        mfcc_proc.flatten()
    )[0, 1]

    # ציון סופי (משוקלל)
    quality_score = min(1.0, max(0.0,
        (snr / 20.0) * 0.6 + spectral_similarity * 0.4
    ))

    return quality_score
```

---

## 4. פלט - קובץ מעובד

### פרמטרי קובץ הפלט
**מיקום:** `/shared/audio/{video_id}/vocals_removed.mp3`
**פורמט טכני:**
- **Codec:** MP3
- **Sample Rate:** זהה לקובץ המקורי
- **Channels:** Mono או Stereo (תלוי באלגוריתם)
- **Bitrate:** 128-192 kbps
- **Content:** אינסטרומנטלי ללא ווקאל

**Schema פלט קובץ:**
```python
@dataclass
class ProcessedAudioFile:
    video_id: str
    output_path: str
    original_path: str
    processing_method: str
    processing_time: float
    quality_score: float
    file_size: int
    created_at: str

def create_processed_file_info(video_id: str, output_path: str,
                             processing_result: dict) -> ProcessedAudioFile:
    return ProcessedAudioFile(
        video_id=video_id,
        output_path=output_path,
        original_path=processing_result.get("original_path"),
        processing_method=processing_result["method"],
        processing_time=processing_result["processing_time"],
        quality_score=processing_result["quality_score"],
        file_size=os.path.getsize(output_path),
        created_at=datetime.utcnow().isoformat()
    )
```

---

## 5. פלט - עדכון Elasticsearch

### עדכון מסמך השיר
**אינדקס:** `songs`
**פעולה:** `UPDATE` (partial document update)

**Schema עדכון:**
```json
{
  "_id": "dQw4w9WgXcQ",
  "doc": {
    "file_paths.vocals_removed": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
    "updated_at": "2025-09-15T10:33:45Z",
    "processing_metadata.audio": {
      "quality_score": 0.85,
      "processing_time": 45.2,
      "method": "demucs",
      "file_size": 5678901
    }
  }
}
```

**Schema Python (Elasticsearch):**
```python
class ElasticsearchUpdate(BaseModel):
    file_paths_vocals_removed: str = Field(..., alias="file_paths.vocals_removed")
    updated_at: str
    processing_metadata_audio: dict = Field(..., alias="processing_metadata.audio")

    class Config:
        allow_population_by_field_name = True

class AudioProcessingMetadata(BaseModel):
    quality_score: float = Field(..., ge=0.0, le=1.0)
    processing_time: float = Field(..., gt=0)
    method: Literal["center_channel_extraction", "demucs", "spleeter"]
    file_size: int = Field(..., gt=0)

def update_elasticsearch_document(video_id: str, output_path: str,
                                processing_result: dict) -> bool:
    """עדכון מסמך Elasticsearch עם נתיבי הקובץ המעובד"""
    update_doc = {
        "file_paths.vocals_removed": output_path,
        "updated_at": datetime.utcnow().isoformat(),
        "processing_metadata.audio": {
            "quality_score": processing_result["quality_score"],
            "processing_time": processing_result["processing_time"],
            "method": processing_result["method"],
            "file_size": processing_result["output_file_size"]
        }
    }

    try:
        es_client.update(
            index="songs",
            id=video_id,
            body={"doc": update_doc}
        )
        return True
    except Exception as e:
        logger.error(f"Failed to update Elasticsearch: {e}")
        return False
```

---

## 6. פלט - הודעת Kafka (הצלחה)

### Kafka Producer - הצלחה
**טופיק:** `audio.vocals_processed`

**Schema הודעה (JSON):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "vocals_processed",
  "vocals_removed_path": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
  "processing_time": 45.2,
  "quality_score": 0.85,
  "method_used": "demucs",
  "file_size": 5678901,
  "timestamp": "2025-09-15T10:33:45Z"
}
```

**Schema Python (Pydantic):**
```python
class AudioProcessedSuccess(BaseModel):
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$')
    status: Literal["vocals_processed"]
    vocals_removed_path: str = Field(..., regex=r'^/shared/audio/.+\.mp3$')
    processing_time: float = Field(..., gt=0, description="Processing time in seconds")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score 0-1")
    method_used: Literal["center_channel_extraction", "demucs", "spleeter"]
    file_size: int = Field(..., gt=0, description="Output file size in bytes")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    class Config:
        schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "status": "vocals_processed",
                "vocals_removed_path": "/shared/audio/dQw4w9WgXcQ/vocals_removed.mp3",
                "processing_time": 45.2,
                "quality_score": 0.85,
                "method_used": "demucs",
                "file_size": 5678901,
                "timestamp": "2025-09-15T10:33:45Z"
            }
        }
```

---

## 7. פלט - הודעת Kafka (שגיאה)

### Kafka Producer - שגיאה
**טופיק:** `audio.processing_failed`

**Schema הודעה (JSON):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "failed",
  "error": {
    "code": "AUDIO_PROCESSING_FAILED",
    "message": "Insufficient audio quality for vocal removal",
    "details": "SNR too low: 2.3dB (minimum required: 10dB)",
    "timestamp": "2025-09-15T10:32:00Z",
    "service": "audio_processing_service"
  },
  "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
  "attempted_method": "demucs",
  "processing_time": 12.5
}
```

**Schema Python (Pydantic):**
```python
class AudioProcessingError(BaseModel):
    code: Literal[
        "FILE_NOT_FOUND",
        "INVALID_AUDIO_FORMAT",
        "AUDIO_QUALITY_TOO_LOW",
        "PROCESSING_TIMEOUT",
        "INSUFFICIENT_MEMORY",
        "DISK_SPACE_ERROR",
        "AUDIO_PROCESSING_FAILED"
    ]
    message: str
    details: Optional[str] = None
    timestamp: str
    service: Literal["audio_processing_service"]

class AudioProcessedError(BaseModel):
    video_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]{11}$')
    status: Literal["failed"]
    error: AudioProcessingError
    original_path: str
    attempted_method: Optional[str] = None
    processing_time: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "status": "failed",
                "error": {
                    "code": "AUDIO_PROCESSING_FAILED",
                    "message": "Insufficient audio quality for vocal removal",
                    "details": "SNR too low: 2.3dB (minimum required: 10dB)",
                    "timestamp": "2025-09-15T10:32:00Z",
                    "service": "audio_processing_service"
                },
                "original_path": "/shared/audio/dQw4w9WgXcQ/original.mp3",
                "attempted_method": "demucs",
                "processing_time": 12.5
            }
        }
```

---

## 8. עדכון מסמך שגיאה ב-Elasticsearch

### עדכון Elasticsearch בשגיאה
```json
{
  "_id": "dQw4w9WgXcQ",
  "doc": {
    "status": "failed",
    "updated_at": "2025-09-15T10:32:00Z",
    "error": {
      "code": "AUDIO_PROCESSING_FAILED",
      "message": "Insufficient audio quality for vocal removal",
      "service": "audio_processing_service",
      "timestamp": "2025-09-15T10:32:00Z"
    },
    "processing_metadata.audio": {
      "attempted_method": "demucs",
      "processing_time": 12.5,
      "error_details": "SNR too low: 2.3dB"
    }
  }
}
```

---

## 9. זרימת המידע המלאה

### תזרים מוצלח:
```
1. Kafka Consumer → קבלת הודעה מ-audio.process.requested
2. File System → קריאת הקובץ המקורי מהנתיב שבהודעה
3. Audio Processing → הסרת ווקאל (demucs/center_channel)
4. File System → שמירת הקובץ המעובד
5. Elasticsearch → עדכון מסמך עם נתיב הקובץ החדש
6. Kafka Producer → שליחת הודעת הצלחה ל-audio.vocals_processed
```

### תזרים עם שגיאה:
```
1. Kafka Consumer → קבלת הודעה מ-audio.process.requested
2. File System → נסיון קריאת הקובץ המקורי (כשל)
3. Error Handling → זיהוי שגיאה וסיווג
4. Elasticsearch → עדכון מסמך עם שגיאה
5. Kafka Producer → שליחת הודעת שגיאה ל-audio.processing_failed
```

---

## 10. תיקון דוקומנטציה נדרש

### הבהרה בדוקומנטציה הקיימת:

**בעיה שזוהתה:** הדוקומנטציה המקורית לא הבהירה מספיק את המקור של נתיבי הקבצים.

**הבהרה נדרשת:**
> **עיקרון חשוב:** שירות עיבוד האודיו **אינו שולף נתיבי קבצים מ-Elasticsearch**. הנתיב לקובץ המקורי מגיע אך ורק דרך הודעת הKafka. השירות שומר את נתיב הקובץ המעובד **רק ב-Elasticsearch** לאחר סיום העיבוד.

### מודל עבודה מומלץ:
1. ✅ **Kafka Input** - קבלת נתיב קובץ מקורי
2. ✅ **File Processing** - עיבוד הקובץ מהנתיב שהתקבל
3. ✅ **Elasticsearch Output** - שמירת נתיב הקובץ המעובד
4. ✅ **Kafka Output** - דיווח על השלמת העיבוד

### אין:
- ❌ שליפת נתיבי קבצים מ-Elasticsearch לפני העיבוד
- ❌ העברת נתיבי קבצים מעובדים דרך Kafka (רק הודעות סטטוס)