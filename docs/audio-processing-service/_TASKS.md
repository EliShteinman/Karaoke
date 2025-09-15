# Audio Processing Service - משימות והסבר

## תפקיד הסרוביס
מבצע הסרת ווקאל מקבצי האודיו המקוריים על בסיס video_id שמתקבל מ-Kafka.

## תזרים עבודה מפורט (Workflow)

### 1. האזנה לבקשות עיבוד
1. **מאזין לטופיק** `audio.process.requested` ב-Kafka
2. **קבלת הודעה** המכילה **רק video_id** (ללא נתיבים!)
3. **ולידציה** של פרמטרי הבקשה

### 2. שליפת נתיב הקובץ המקורי
1. **פונה ל-Elasticsearch** עם ה-video_id שקיבל מ-Kafka
2. **שולף מהמסמך** את נתיב הקובץ `file_paths.original`
3. **בדיקת תקינות** הנתיב וקיום הקובץ

### 3. טעינה ועיבוד הקובץ
1. **קורא את הקובץ** `original.mp3` מה-Shared Storage לפי הנתיב שנשלף
2. **בדיקת תקינות** הקובץ (פורמט, איכות, משך)
3. **טעינת הקובץ** לזיכרון לעיבוד

### 4. הסרת ווקאל
1. **ניתוח ספקטרלי** של הקובץ לזיהוי תדרי ווקאל
2. **הפרדת ערוצים** (Left/Right) וזיהוי המרכז הסטריאו
3. **יישום אלגוריתם Center Channel Extraction:**
   - חיסור הערוץ הימני מהשמאלי
   - פילטור תדרים גבוהים (ווקאל)
   - שמירה על כלי נגינה בתדרים נמוכים
4. **נורמליזציה** של הקובץ המעובד
5. **הערכת איכות** התוצר (Quality Score)

### 5. שמירה ועדכון
1. **שומר את התוצר** בנתיב `shared/audio/{video_id}/vocals_removed.mp3`
2. **מעדכן את מסמך השיר** ב-Elasticsearch עם הנתיב החדש
3. **שולח אירוע סיום** לטופיק `audio.vocals_processed` (ללא נתיבים!)

## תקשורת עם שירותים אחרים

### עם Kafka
- **מאזין:** טופיק `audio.process.requested` (קבלת video_id בלבד)
- **שולח:** טופיק `audio.vocals_processed` (דיווח סיום ללא נתיבים)
- **שולח שגיאות:** טופיק `audio.processing.failed` במקרה של כשל

### עם Elasticsearch
- **קורא:** נתיב הקובץ המקורי (`file_paths.original`) לפי video_id
- **מעדכן:** שדה `file_paths.vocals_removed` במסמך השיר
- **מעדכן:** שדות `processing_metadata.audio` עם נתוני עיבוד

### עם Shared Storage
- **קורא:** קבצי אודיו מקוריים לפי הנתיב שנשלף מ-Elasticsearch
- **כותב:** קבצי אודיו מעובדים לנתיב `/shared/audio/{video_id}/vocals_removed.mp3`

### עם Audio Processing Libraries
- **משתמש:** librosa לניתוח אודיו ועיבוד ספקטרלי
- **משתמש:** numpy ו-scipy לחישובים מתמטיים
- **משתמש:** FFmpeg לקריאה וכתיבה של קבצי אודיו

## רשימת משימות פיתוח

### Phase 1: תשתית אודיו בסיסית
- [ ] הקמת פרויקט Python עם תלויות אודיו (librosa, numpy, scipy)
- [ ] יישום קריאה וכתיבה בסיסית של קבצי MP3
- [ ] ולידציה של פורמטים ואיכות אודיו
- [ ] הגדרת logging מפורט לתהליכי עיבוד
- [ ] יצירת unit tests לפונקציות אודיו בסיסיות

### Phase 2: אלגוריתמי הסרת ווקאל
- [ ] יישום Center Channel Extraction הבסיסי
- [ ] הוספת פילטרים תדר מתקדמים
- [ ] אלגוריתם הערכת איכות (Quality Score)
- [ ] אופטימיזציה לזמני עיבוד
- [ ] בדיקות השוואה עם קבצי reference

### Phase 3: אינטגרציה עם Kafka (רק video_id)
- [ ] יישום Kafka consumer לטופיק `audio.process.requested`
- [ ] **ולידציה שההודעה מכילה רק video_id** (ללא נתיבים)
- [ ] יישום Kafka producer לאירועי סיום (ללא נתיבים)
- [ ] הגדרת serialization/deserialization של הודעות
- [ ] טיפול בשגיאות תקשורת ו-retry logic
- [ ] הוספת idempotency למניעת עיבוד כפול

### Phase 4: אינטגרציה עם Elasticsearch
- [ ] הקמת Elasticsearch client לקריאה ועדכונים
- [ ] **יישום שליפת נתיב הקובץ המקורי לפי video_id**
- [ ] יישום partial updates למסמכי שירים
- [ ] הוספת מטאדאטה מפורטת על העיבוד
- [ ] ניהול שגיאות כתיבה וretry mechanism
- [ ] סנכרון בין מצב הקובץ למסמך

### Phase 5: ניהול קבצים ואחסון
- [ ] **שליפת נתיבי קבצים דינמית מ-Elasticsearch**
- [ ] וידוא תקינות קבצי קלט וקיומם
- [ ] cleanup של קבצים זמניים ושגיאות
- [ ] compression ואופטימיזציה של קבצי פלט
- [ ] backup ו-recovery של קבצים חשובים

### Phase 6: ביצועים ואמינות
- [ ] עיבוד מקבילי של קבצים מרובים
- [ ] אופטימיזציה של זיכרון לקבצים גדולים
- [ ] ניטור ביצועים ו-resource usage
- [ ] circuit breaker למניעת overload
- [ ] health checks ו-monitoring endpoints

### Phase 7: ניהול שגיאות מתקדם
- [ ] זיהוי וטיפול בקבצי אודיו פגומים
- [ ] **טיפול בשגיאות שליפת נתיבים מ-Elasticsearch**
- [ ] recovery מכשלים חלקיים
- [ ] ניהול תדרי עיבוד עמוסים
- [ ] alerting למצבי כשל חמורים
- [ ] fallback mechanisms לאלגוריתמים חלופיים

### Phase 8: תיעוד ואינטגרציה
- [ ] תיעוד מפורט של אלגוריתמי העיבוד
- [ ] דוגמאות ו-tutorials לשימוש
- [ ] integration tests עם השירותים האחרים
- [ ] מדידת ביצועים ו-benchmarking
- [ ] הכנת deployment guides

## דרישות טכניות

### תלויות עיקריות
- **librosa**: ניתוח ועיבוד אודיו מתקדם
- **numpy**: חישובים מתמטיים וmarray manipulation
- **scipy**: עיבוד אותות דיגיטליים וFourier transforms
- **soundfile**: קריאה וכתיבה של קבצי אודיו
- **kafka-python**: תקשורת עם Kafka
- **elasticsearch**: קריאה ועדכון מסמכים
- **pydub**: עיבוד אודיו ברמה גבוהה (אופציונלי)

### משתני סביבה נדרשים
```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=audio_processing_group
KAFKA_AUDIO_TOPIC=audio.process.requested
KAFKA_OUTPUT_TOPIC=audio.vocals_processed

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=songs

# Storage
SHARED_STORAGE_PATH=/shared/audio

# Audio Processing
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=2
AUDIO_BIT_DEPTH=16
QUALITY_THRESHOLD=0.7

# Performance
MAX_CONCURRENT_JOBS=4
MEMORY_LIMIT_MB=2048
PROCESSING_TIMEOUT_MINUTES=10
```

### פרמטרי עיבוד אודיו
```python
audio_processing_config = {
    # Center Channel Extraction
    "vocal_isolation": {
        "method": "center_channel_extraction",
        "low_cut_freq": 100,      # Hz
        "high_cut_freq": 8000,    # Hz
        "vocal_reduction": 0.85,  # אחוז הפחתת ווקאל
        "preserve_stereo": True
    },

    # Quality Control
    "quality_metrics": {
        "min_snr": 10,           # dB
        "max_distortion": 0.15,  # אחוז עיוות מקסימלי
        "frequency_balance": 0.85 # איזון תדרים
    },

    # Output Settings
    "output": {
        "format": "mp3",
        "bitrate": "128k",
        "sample_rate": 44100,
        "normalize": True
    }
}
```

### מבנה קבצים מומלץ
```
audio-processing-service/
├── app/
│   ├── main.py                    # נקודת כניסה
│   ├── services/
│   │   ├── vocal_remover.py       # אלגוריתמי הסרת ווקאל
│   │   ├── audio_analyzer.py      # ניתוח איכות ומטרין
│   │   ├── file_processor.py      # ניהול קבצים
│   │   └── elasticsearch_updater.py
│   ├── consumers/
│   │   └── audio_consumer.py      # Kafka consumer
│   ├── models/
│   │   ├── audio_models.py        # מבני נתונים
│   │   └── processing_results.py   # תוצאות עיבוד
│   ├── algorithms/
│   │   ├── center_channel.py      # אלגוריתם עיקרי
│   │   ├── spectral_analysis.py   # ניתוח ספקטרלי
│   │   └── quality_assessment.py  # הערכת איכות
│   ├── config/
│   │   ├── settings.py
│   │   └── audio_config.py        # הגדרות עיבוד
│   └── utils/
│       ├── logger.py
│       ├── file_utils.py
│       └── performance_utils.py
├── tests/
│   ├── test_vocal_removal.py
│   ├── test_audio_quality.py
│   └── fixtures/                  # קבצי בדיקה
└── requirements.txt
```

### דרישות חומרה
- **זיכרון RAM**: מינימום 2GB פנויים לעיבוד
- **מעבד**: ליבות מרובות מומלצות (4+ cores)
- **אחסון**: 10GB פנויים למטמון זמני
- **רשת**: חיבור יציב לשירותי התשתית

## עקרונות ארכיטקטורליים קריטיים

### חוק Single Source of Truth
- **Kafka מכיל רק video_id** - ללא נתיבי קבצים
- **נתיבי קבצים נשלפים תמיד מ-Elasticsearch**
- זה מבטיח שרק Elasticsearch הוא מקור האמת לנתיבים

### זרימת עבודה נכונה
1. **Kafka:** קבלת video_id בלבד
2. **Elasticsearch:** שליפת `file_paths.original`
3. **File System:** קריאת קובץ לפי הנתיב הנשלף
4. **Processing:** יצירת קובץ מעובד עם שם קבוע
5. **Elasticsearch:** עדכון `file_paths.vocals_removed`
6. **Kafka:** דיווח סיום (ללא נתיבים)

### דוגמה לקוד נכון
```python
# ✅ נכון - שליפת נתיב מ-Elasticsearch
def process_audio(video_id: str):
    # שלב 1: שליפת נתיב מ-Elasticsearch
    doc = elasticsearch.get(index="songs", id=video_id)
    original_path = doc["_source"]["file_paths"]["original"]

    # שלב 2: עיבוד הקובץ
    vocals_removed_path = f"/shared/audio/{video_id}/vocals_removed.mp3"
    process_vocal_removal(original_path, vocals_removed_path)

    # שלב 3: עדכון Elasticsearch
    elasticsearch.update(
        index="songs",
        id=video_id,
        body={"doc": {"file_paths.vocals_removed": vocals_removed_path}}
    )

    # שלב 4: דיווח ל-Kafka (ללא נתיבים)
    kafka_producer.send("audio.vocals_processed", {
        "video_id": video_id,
        "status": "vocals_processed"
    })

# ❌ שגוי - נתיב מגיע מ-Kafka
def process_audio_wrong(kafka_message):
    original_path = kafka_message["original_path"]  # אסור!
```