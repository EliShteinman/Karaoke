# Infrastructure - מנהל פרויקט

## המשימה שלך
את/ה אחראי/ת על התשתית המשותפת ותיאום הפרויקט.

## הענף שלך: `feature/shared-infrastructure`

## מה עליך לעשות:
1. השלם את הקוד המשותף ב-shared/
2. וודא אינטגרציה בין השירותים
3. נהל Kafka topics ו-schemas
4. הגדר Kubernetes deployment
5. כתוב documentation מלא

## המבנה שלך:
```
shared/ (כבר קיים עם שלדים)
├── utils/logger.py         # השלם את הלוגיקה
├── kafka/producer.py       # השלם את הלוגיקה
├── kafka/consumer.py       # השלם את הלוגיקה
├── mongodb/client.py       # השלם את הלוגיקה
├── elasticsearch/client.py # השלם את הלוגיקה
└── models/song.py          # השלם אם נדרש

infrastructure/
├── docker/                 # קבצים שלך לכתוב
│   ├── kafka-topics.sh
│   └── init-databases.sh
└── kubernetes/             # קבצים שלך לכתוב
    ├── namespace.yaml
    ├── kafka.yaml
    ├── mongodb.yaml
    ├── elasticsearch.yaml
    └── services/
        ├── downloader.yaml
        ├── processor.yaml
        ├── transcriber.yaml
        ├── lrc-generator.yaml
        └── ui.yaml
```

## קבצים שעליך לכתוב/להשלים:

### Docker Scripts
- `kafka-topics.sh` - יצירת topics אוטומטית
- `init-databases.sh` - אתחול MongoDB ו-Elasticsearch

### Kubernetes Manifests
- כל ה-YAML files לדפלויםנט
- ConfigMaps ו-Secrets
- Services ו-Ingress

### Shared Code
- השלם את כל ה-TODOs ב-shared/
- וודא שהקוד עובד עם כל השירותים

## Kafka Topics שעליך ליצור:
```bash
youtube_download_requests
audio_processing_requests
transcription_requests
lrc_generation_requests
ui_notifications
```

## MongoDB Collections:
```
songs_metadata
audio_files (GridFS)
transcription_results
lrc_files
processing_status
```

## Elasticsearch Indices:
```
songs-metadata
processing-logs
search-index
```

## Docker Commands:
```bash
# הרצת התשתית
docker-compose up -d kafka mongodb elasticsearch redis

# הרצת כל השירותים
docker-compose up --build

# אתחול databases
./infrastructure/docker/init-databases.sh

# יצירת Kafka topics
./infrastructure/docker/kafka-topics.sh
```

## Kubernetes Deployment:
```bash
# יצירת namespace
kubectl apply -f infrastructure/kubernetes/namespace.yaml

# דפלוי התשתית
kubectl apply -f infrastructure/kubernetes/

# דפלוי השירותים
kubectl apply -f infrastructure/kubernetes/services/
```

## אחריויות נוספות:
- **תיאום צוותים** - וודא שכולם עובדים טוב יחד
- **Code review** - בדוק PR של כל המפתחים
- **Integration testing** - בדוק שהכל עובד מקצה לקצה
- **Documentation** - כתוב מדריכים והסברים
- **Monitoring** - הוסף לוגים ומטריקות

## כלים לניהול:
- Git - ניהול ברנצ'ים ו-merges
- Docker Compose - הרצה מקומית
- Kubernetes - פרודקשן
- Kafka UI - ניהול topics
- MongoDB Compass - ניהול DB

**בהצלחה עם הניהול! 🎯**