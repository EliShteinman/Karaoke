# Transcription Service - משימות והסבר

## תפקיד הסרוביס
מבצע תמלול השירים ויוצר קבצי כתוביות LRC עם סנכרון זמן מדויק על בסיס video_id שמתקבל מ-Kafka.

## תזרים עבודה מפורט (Workflow)

### 1. האזנה לבקשות תמלול
1. **מאזין לטופיק** `transcription.process.requested` ב-Kafka
2. **קבלת הודעה** המכילה **רק video_id** (ללא נתיבים!)
3. **ולידציה** של פרמטרי הבקשה והודעה

### 2. שליפת נתיב הקובץ המקורי
1. **פונה ל-Elasticsearch** עם ה-video_id שקיבל מ-Kafka
2. **שולף מהמסמך** את נתיב הקובץ `file_paths.original`
3. **בדיקת תקינות** הנתיב וקיום הקובץ

### 3. טעינה והכנת הקובץ
1. **קורא את הקובץ** `original.mp3` מה-Shared Storage לפי הנתיב שנשלף
2. **בדיקת תקינות** הקובץ (פורמט, איכות, משך, קיום ווקאל)
3. **עיבוד מקדים** של הקובץ לתמלול (המרה ל-16kHz mono אם נדרש)

### 4. תמלול השיר
1. **עדכון תחילת תמלול:** `status.transcription: "in_progress"`
2. **טעינת מודל** Whisper Large v3 (או מטמון קיים)
3. **זיהוי שפה** אוטומטי (בעיקר אנגלית)
4. **Voice Activity Detection** לזיהוי קטעי שירה vs. כלי נגינה
5. **תמלול מלא** עם timestamps ברמת מילה
6. **הערכת אמינות** התמלול (confidence score)

### 5. יצירת קובץ LRC
1. **פילוח לשורות** על בסיס הפסקות ומשפטים
2. **סנכרון timestamps** עם מבנה שירה טיפוסי
3. **הוספת מטאדאטה** לקובץ LRC (אמן, כותרת, משך)
4. **ולידציה** של מבנה הקובץ ותקינות הזמנים
5. **אופטימיזציה** למסכי קריוקי (אורך שורות, מהירות קריאה)

### 6. שמירה ועדכון
1. **שומר את התוצר** בנתיב `shared/audio/{video_id}/lyrics.lrc`
2. **מעדכן את מסמך השיר** ב-Elasticsearch:
   - `status.transcription: "completed"`
   - **אם כל השלבים הושלמו:** `status.overall: "completed"`
   - הנתיב החדש והמטאדאטה
3. **שולח אירוע סיום** לטופיק `transcription.done` (ללא נתיבים!)

## תקשורת עם שירותים אחרים

### עם Kafka
- **מאזין:** טופיק `transcription.process.requested` (קבלת video_id בלבד)
- **שולח:** טופיק `transcription.done` (דיווח סיום ללא נתיבים)
- **שולח שגיאות:** טופיק `transcription.failed` במקרה של כשל

### עם Elasticsearch
- **קורא:** נתיב הקובץ המקורי (`file_paths.original`) לפי video_id
- **מעדכן:** שדה `file_paths.lyrics` במסמך השיר
- **מעדכן:** שדות `processing_metadata.transcription` עם נתוני תמלול

### עם Shared Storage
- **קורא:** קבצי אודיו מקוריים לפי הנתיב שנשלף מ-Elasticsearch
- **כותב:** קבצי כתוביות LRC לנתיב `/shared/audio/{video_id}/lyrics.lrc`

### עם OpenAI Whisper
- **טוען:** מודלי Speech-to-Text (Whisper Large v3)
- **מבצע:** תמלול עם timestamps מדויקים
- **מקבל:** תוצאות תמלול JSON עם confidence scores

## רשימת משימות פיתוח

### Phase 1: תשתית Speech-to-Text
- [ ] הקמת פרויקט Python עם Whisper ותלויות
- [ ] הורדה והתקנה של מודלי Whisper
- [ ] יישום תמלול בסיסי עם timestamps
- [ ] ולידציה של פורמטי אודיו נתמכים
- [ ] הגדרת caching למודלים להאצת טעינה

### Phase 2: עיבוד אודיו מתקדם
- [ ] יישום Voice Activity Detection (VAD)
- [ ] זיהוי והפרדה של קטעי שירה מכלי נגינה
- [ ] אופטימיזציה של איכות אודיו לתמלול
- [ ] ניהול קבצי אודיו ארוכים (חלוקה לחלקים)
- [ ] רמת confidence ואמינות לכל מילה ומשפט

### Phase 3: יצירת קבצי LRC
- [ ] parser ו-generator לפורמט LRC
- [ ] אלגוריתמי פילוח לשורות מבוסס משמעות
- [ ] סנכרון timestamps מדויק עם מבנה שירה
- [ ] הוספת מטאדאטה (אמן, כותרת, אלבום)
- [ ] ולידציה ותיקון שגיאות פורמט

### Phase 4: אינטגרציה עם Kafka (רק video_id)
- [ ] יישום Kafka consumer לטופיק `transcription.process.requested`
- [ ] **ולידציה שההודעה מכילה רק video_id** (ללא נתיבים)
- [ ] יישום Kafka producer לאירועי סיום (ללא נתיבים)
- [ ] הגדרת serialization/deserialization של הודעות
- [ ] טיפול בשגיאות תקשורת ו-retry logic
- [ ] הוספת idempotency למניעת תמלול כפול

### Phase 5: אינטגרציה עם Elasticsearch
- [ ] הקמת Elasticsearch client לקריאה ועדכונים
- [ ] **יישום שליפת נתיב הקובץ המקורי לפי video_id**
- [ ] יישום partial updates למסמכי שירים
- [ ] הוספת מטאדאטה מפורטת על התמלול
- [ ] ניהול שגיאות כתיבה וretry mechanism
- [ ] סנכרון בין מצב הקובץ למסמך

### Phase 6: איכות ואמינות
- [ ] הערכת איכות תמלול וזיהוי כשלים
- [ ] fallback לשיטות תמלול חלופיות
- [ ] post-processing לשיפור דיוק הטקסט
- [ ] זיהוי ותיקון שגיאות תמלול נפוצות
- [ ] בדיקות השוואה עם כתוביות reference

### Phase 7: ביצועים ואופטימיזציה
- [ ] עיבוד מקבילי של קבצים מרובים
- [ ] אופטימיזציה של זיכרון ו-GPU usage
- [ ] streaming processing לקבצים גדולים
- [ ] ניטור ביצועים ו-resource usage
- [ ] cache optimization למודלים ותוצאות

### Phase 8: ניהול שגיאות ומעקב
- [ ] זיהוי וטיפול בקבצי אודיו ללא ווקאל
- [ ] **טיפול בשגיאות שליפת נתיבים מ-Elasticsearch**
- [ ] ניהול שפות לא נתמכות
- [ ] recovery מכשלים חלקיים
- [ ] alerting למצבי כשל או איכות נמוכה
- [ ] health checks ו-monitoring endpoints

### Phase 9: תיעוד ואינטגרציה
- [ ] תיעוד מפורט של אלגוריתמי התמלול
- [ ] דוגמאות ו-tutorials לשימוש
- [ ] integration tests עם השירותים האחרים
- [ ] מדידת ביצועים ו-benchmarking
- [ ] הכנת deployment guides

## דרישות טכניות

### תלויות עיקריות
- **openai-whisper**: מודל Speech-to-Text מתקדם
- **torch**: PyTorch לרשתות נוירליות
- **librosa**: עיבוד אודיו וניתוח
- **soundfile**: קריאה וכתיבה של קבצי אודיו
- **webrtcvad**: Voice Activity Detection
- **kafka-python**: תקשורת עם Kafka
- **elasticsearch**: קריאה ועדכון מסמכים

### משתני סביבה נדרשים
```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=transcription_service_group
KAFKA_TRANSCRIPTION_TOPIC=transcription.process.requested
KAFKA_OUTPUT_TOPIC=transcription.done

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=songs

# Storage
SHARED_STORAGE_PATH=/shared/audio

# Whisper Configuration
WHISPER_MODEL=large-v3
WHISPER_LANGUAGE=auto
WHISPER_DEVICE=auto
WHISPER_MODELS_DIR=/models/whisper

# Transcription Settings
MIN_CONFIDENCE_THRESHOLD=0.7
MAX_AUDIO_DURATION_MINUTES=15
VAD_AGGRESSIVENESS=2
PROCESSING_TIMEOUT_MINUTES=20

# Performance
MAX_CONCURRENT_JOBS=2
GPU_MEMORY_LIMIT_GB=6
CPU_THREADS=4
```

### הגדרות Whisper מתקדמות
```python
whisper_config = {
    # Model Settings
    "model": "large-v3",
    "device": "auto",          # auto/cpu/cuda
    "download_root": "/models/whisper",

    # Transcription Parameters
    "language": "auto",        # זיהוי שפה אוטומטי
    "task": "transcribe",      # לא translate
    "temperature": 0.0,        # דטרמיניסטי
    "beam_size": 5,           # חיפוש קרן
    "best_of": 1,             # מספר ניסיונות
    "patience": 1.0,          # סבלנות לhallucination

    # Advanced Features
    "word_timestamps": True,   # timestamps ברמת מילה
    "prepend_punctuations": "\"'"¿([{-",
    "append_punctuations": "\"'.。,，!！?？:：")]}、",

    # VAD Settings
    "vad_filter": True,
    "vad_parameters": {
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "max_speech_duration_s": 30,
        "min_silence_duration_ms": 2000,
        "speech_pad_ms": 400
    }
}
```

### פורמט קובץ LRC
```python
lrc_format = {
    # Header Metadata
    "metadata": {
        "ar": "Artist Name",          # [ar:Artist]
        "ti": "Song Title",           # [ti:Title]
        "al": "Album Name",           # [al:Album]
        "au": "Author",               # [au:Author]
        "length": "03:33",            # [length:mm:ss]
        "by": "transcription_service", # [by:Creator]
        "offset": "0"                 # [offset:+/-100]
    },

    # Lyrics with Timestamps
    "lyrics": [
        "[00:12.50]Example lyric line",
        "[00:16.80]Next line of lyrics",
        "[00:20.90]And so on..."
    ],

    # Formatting Rules
    "rules": {
        "timestamp_format": "[mm:ss.xx]",
        "max_line_length": 60,
        "min_line_duration": 1.0,     # שניות
        "max_line_duration": 8.0,     # שניות
        "early_display": 0.5          # הצגה מוקדמת
    }
}
```

### מבנה קבצים מומלץ
```
transcription-service/
├── app/
│   ├── main.py                    # נקודת כניסה
│   ├── services/
│   │   ├── speech_to_text.py      # תמלול עם Whisper
│   │   ├── lrc_generator.py       # יצירת קבצי LRC
│   │   ├── audio_preprocessor.py  # עיבוד מקדים
│   │   ├── vad_processor.py       # Voice Activity Detection
│   │   └── elasticsearch_updater.py
│   ├── consumers/
│   │   └── transcription_consumer.py # Kafka consumer
│   ├── models/
│   │   ├── transcription_models.py   # מבני נתונים
│   │   ├── lrc_models.py             # מודל קובץ LRC
│   │   └── whisper_results.py        # תוצאות Whisper
│   ├── algorithms/
│   │   ├── text_segmentation.py      # חלוקה לשורות
│   │   ├── timestamp_alignment.py    # סנכרון זמנים
│   │   └── quality_assessment.py     # הערכת איכות
│   ├── config/
│   │   ├── settings.py
│   │   ├── whisper_config.py         # הגדרות Whisper
│   │   └── lrc_config.py             # הגדרות LRC
│   └── utils/
│       ├── logger.py
│       ├── file_utils.py
│       ├── text_utils.py
│       └── performance_utils.py
├── models/                           # מודלי Whisper
├── tests/
│   ├── test_transcription.py
│   ├── test_lrc_generation.py
│   └── fixtures/                     # קבצי בדיקה
└── requirements.txt
```

### דרישות חומרה
- **זיכרון RAM**: מינימום 8GB (לWhisper Large)
- **GPU**: מומלץ NVIDIA עם 6GB+ VRAM
- **מעבד**: ליבות מרובות מומלצות (8+ cores)
- **אחסון**: 5GB למודלי Whisper + 10GB למטמון

## עקרונות ארכיטקטורליים קריטיים

### חוק Single Source of Truth
- **Kafka מכיל רק video_id** - ללא נתיבי קבצים
- **נתיבי קבצים נשלפים תמיד מ-Elasticsearch**
- זה מבטיח שרק Elasticsearch הוא מקור האמת לנתיבים

### זרימת עבודה נכונה
1. **Kafka:** קבלת video_id בלבד
2. **Elasticsearch:** שליפת `file_paths.original`
3. **File System:** קריאת קובץ לפי הנתיב הנשלף
4. **Processing:** יצירת קובץ LRC עם שם קבוע
5. **Elasticsearch:** עדכון `file_paths.lyrics`
6. **Kafka:** דיווח סיום (ללא נתיבים)

### דוגמה לקוד נכון
```python
# ✅ נכון - שליפת נתיב מ-Elasticsearch
def process_transcription(video_id: str):
    # שלב 1: שליפת נתיב מ-Elasticsearch
    doc = elasticsearch.get(index="songs", id=video_id)
    original_path = doc["_source"]["file_paths"]["original"]

    # שלב 2: תמלול הקובץ
    lyrics_path = f"/shared/audio/{video_id}/lyrics.lrc"
    transcribe_audio_to_lrc(original_path, lyrics_path)

    # שלב 3: עדכון Elasticsearch
    elasticsearch.update(
        index="songs",
        id=video_id,
        body={"doc": {"file_paths.lyrics": lyrics_path}}
    )

    # שלב 4: דיווח ל-Kafka (ללא נתיבים)
    kafka_producer.send("transcription.done", {
        "video_id": video_id,
        "status": "transcription_done"
    })

# ❌ שגוי - נתיב מגיע מ-Kafka
def process_transcription_wrong(kafka_message):
    original_path = kafka_message["original_path"]  # אסור!
```