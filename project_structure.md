# מבנה קבצים מומלץ - פרויקט קריוקי

```
karaoke-system/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── shared/                           # קוד משותף בין השירותים
│   ├── __init__.py
│   ├── models/                       # מודלים משותפים
│   │   ├── __init__.py
│   │   ├── song.py                   # Song dataclass/model
│   │   ├── kafka_messages.py         # Kafka message schemas
│   │   └── elasticsearch_schemas.py  # Elasticsearch mappings
│   ├── config/                       # הגדרות משותפות
│   │   ├── __init__.py
│   │   ├── settings.py               # Environment variables
│   │   ├── kafka_config.py           # Kafka connection settings
│   │   └── elasticsearch_config.py   # Elasticsearch connection
│   ├── utils/                        # פונקציות עזר משותפות
│   │   ├── __init__.py
│   │   ├── logger.py                 # Logging setup
│   │   ├── file_utils.py             # File operations
│   │   └── validation.py             # Input validation
│   └── clients/                      # לקוחות משותפים
│       ├── __init__.py
│       ├── kafka_client.py           # Kafka producer/consumer wrapper
│       └── elasticsearch_client.py   # Elasticsearch client wrapper
│
├── services/                         # המיקרו-סרביסים
│   ├── api-server/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # FastAPI app entry point
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── search.py         # POST /search
│   │   │   │   ├── download.py       # POST /download
│   │   │   │   ├── songs.py          # GET /songs, GET /songs/{id}
│   │   │   │   └── health.py         # Health check endpoints
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── song_service.py   # Business logic
│   │   │   │   └── elasticsearch_service.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── requests.py       # Pydantic request models
│   │   │       └── responses.py      # Pydantic response models
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_routes.py
│   │       └── test_services.py
│   │
│   ├── youtube-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py               # Service entry point
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── youtube_search.py # YouTube API integration
│   │   │   │   ├── youtube_download.py # YTDLP integration
│   │   │   │   └── kafka_producer.py # Kafka message sending
│   │   │   ├── consumers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── download_consumer.py # Kafka consumer
│   │   │   └── config/
│   │   │       ├── __init__.py
│   │   │       └── youtube_config.py # YouTube API keys
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_search.py
│   │       └── test_download.py
│   │
│   ├── audio-processing-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vocal_remover.py  # Core audio processing
│   │   │   │   └── elasticsearch_updater.py
│   │   │   ├── consumers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── audio_consumer.py # Kafka consumer
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── audio_models.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_vocal_removal.py
│   │
│   ├── transcription-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── speech_to_text.py # STT + timestamp sync
│   │   │   │   ├── lrc_generator.py  # LRC file creation
│   │   │   │   └── elasticsearch_updater.py
│   │   │   ├── consumers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── transcription_consumer.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── transcription_models.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_transcription.py
│   │
│   └── streamlit-client/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py               # Streamlit app entry
│       │   ├── pages/
│       │   │   ├── __init__.py
│       │   │   ├── search.py         # Search page
│       │   │   ├── player.py         # Karaoke player page
│       │   │   └── library.py        # Songs library page
│       │   ├── components/
│       │   │   ├── __init__.py
│       │   │   ├── search_form.py    # Search UI component
│       │   │   ├── player_controls.py # Player UI component
│       │   │   └── lyrics_display.py # Lyrics sync component
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── api_client.py     # API Server client
│       │   │   ├── audio_player.py   # Audio playback logic
│       │   │   └── lrc_parser.py     # LRC file parsing
│       │   └── utils/
│       │       ├── __init__.py
│       │       ├── session_state.py  # Streamlit session management
│       │       └── file_handlers.py  # File download/upload
│       └── tests/
│           ├── __init__.py
│           └── test_components.py
│
├── infrastructure/                   # תשתית ו-DevOps
│   ├── kafka/
│   │   ├── docker-compose.kafka.yml
│   │   └── topics-setup.sh           # Kafka topics creation script
│   ├── elasticsearch/
│   │   ├── docker-compose.elasticsearch.yml
│   │   ├── mappings/
│   │   │   └── songs-mapping.json    # Elasticsearch index mapping
│   │   └── init-scripts/
│   │       └── create-index.sh
│   ├── monitoring/
│   │   ├── docker-compose.monitoring.yml
│   │   ├── prometheus/
│   │   │   └── prometheus.yml
│   │   └── grafana/
│   │       └── dashboards/
│   └── nginx/
│       ├── nginx.conf                # Reverse proxy config
│       └── ssl/                      # SSL certificates
│
├── data/                             # נתונים ומשאבים
│   ├── shared-storage/               # Volume mount point
│   │   └── audio/                    # יתוקן על ידי docker-compose
│   ├── elasticsearch-data/          # Elasticsearch persistence
│   └── kafka-data/                   # Kafka persistence
│
├── scripts/                          # סקריפטים עזר
│   ├── setup.sh                      # Project setup script
│   ├── start-all.sh                  # Start all services
│   ├── stop-all.sh                   # Stop all services
│   ├── clean-data.sh                 # Clean volumes
│   └── test-all.sh                   # Run all tests
│
├── docs/                             # תיעוד
│   ├── api/                          # API documentation
│   │   ├── openapi.yml               # OpenAPI spec
│   │   └── postman-collection.json
│   ├── architecture/
│   │   ├── system-overview.md
│   │   └── microservices-spec.md     # הקבצים שכבר יש לך
│   └── deployment/
│       ├── local-setup.md
│       └── production-setup.md
│
└── tests/                            # Integration tests
    ├── __init__.py
    ├── integration/
    │   ├── __init__.py
    │   ├── test_full_flow.py          # End-to-end tests
    │   └── test_kafka_integration.py
    ├── performance/
    │   ├── __init__.py
    │   └── load_tests.py
    └── fixtures/
        ├── __init__.py
        ├── sample_songs.json
        └── test_audio_files/
```

## הערות חשובות:

### 📦 **תיקיית `shared/`**
- **מטרה:** קוד משותף שכל השירותים משתמשים בו
- **התקנה:** כל שירות יכלול את `shared/` כ-dependency
- **גישה:** `from shared.models.song import Song`

### 🐳 **Docker Structure**
- כל שירות עם Dockerfile נפרד
- `docker-compose.yml` ראשי מחבר הכל
- Volumes משותפים ל-`/data/shared-storage`

### 🔧 **Configuration**
- `.env.example` מכיל דוגמאות למשתני סביבה
- כל שירות קורא את ההגדרות מ-`shared/config/`

### 🧪 **Testing Strategy**
- Unit tests בתוך כל שירות
- Integration tests בשורש הפרויקט
- E2E tests ב-`tests/integration/`

### 📚 **Package Management**
הוספת `shared/` כ-dependency לכל שירות:
```dockerfile
# In each service's Dockerfile
COPY shared/ /app/shared/
COPY services/[service-name]/ /app/
```