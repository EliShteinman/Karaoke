# Configuration Guide - HebKaraoke Project

Complete guide for all environment variables and configuration settings for all services.

## 📋 Overview

The project uses environment variables to configure all services. Each service can work with defaults or custom settings.

## ⚙️ Environment Variables by Service

### 📡 Kafka Configuration

```bash
# Kafka server connection
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Project topic names
KAFKA_TOPIC_DOWNLOAD_REQUESTED=song.download.requested
KAFKA_TOPIC_DOWNLOADED=song.downloaded
KAFKA_TOPIC_AUDIO_PROCESS=audio.process.requested
KAFKA_TOPIC_VOCALS_PROCESSED=audio.vocals_processed
KAFKA_TOPIC_TRANSCRIPTION=transcription.process.requested
KAFKA_TOPIC_TRANSCRIPTION_DONE=transcription.done

# Consumer groups
KAFKA_CONSUMER_GROUP_YOUTUBE=youtube-service
KAFKA_CONSUMER_GROUP_AUDIO=audio-service
KAFKA_CONSUMER_GROUP_TRANSCRIPTION=transcription-service
```

### 🔍 Elasticsearch Configuration

```bash
# Connection settings
ELASTICSEARCH_SCHEME=http                    # or https
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic              # optional
ELASTICSEARCH_PASSWORD=password123          # optional

# Index names
ELASTICSEARCH_SONGS_INDEX=songs
ELASTICSEARCH_LOGS_INDEX=logs
```

### 💾 File Storage Configuration

```bash
# File storage
STORAGE_BASE_PATH=/shared                   # base path for volume
STORAGE_TYPE=volume                         # volume or s3

# S3 settings (future use)
STORAGE_S3_BUCKET=my-karaoke-bucket
STORAGE_S3_REGION=us-east-1
STORAGE_S3_ACCESS_KEY=YOUR_ACCESS_KEY
STORAGE_S3_SECRET_KEY=YOUR_SECRET_KEY
```

### 📝 Logger Configuration

```bash
# Logging settings
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Elasticsearch logging
LOG_ELASTICSEARCH_ENABLED=true
LOG_ELASTICSEARCH_SCHEME=http
LOG_ELASTICSEARCH_HOST=localhost
LOG_ELASTICSEARCH_PORT=9200
LOG_ELASTICSEARCH_INDEX=logs
```

### 🎵 YouTube Service Configuration

```bash
# YouTube API
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
YOUTUBE_MAX_RESULTS=10

# Download settings
YOUTUBE_DOWNLOAD_QUALITY=bestaudio
YOUTUBE_DOWNLOAD_FORMAT=mp3
```

### 🎤 Audio Service Configuration

```bash
# Audio processing
AUDIO_VOCAL_REMOVAL_METHOD=spleeter         # spleeter, uvr, etc.
AUDIO_OUTPUT_FORMAT=mp3
AUDIO_SAMPLE_RATE=44100
AUDIO_BITRATE=128k
```

### 🗣️ Transcription Service Configuration

```bash
# Speech recognition
TRANSCRIPTION_MODEL_NAME=whisper-base       # whisper-tiny, whisper-base, etc.
TRANSCRIPTION_LANGUAGE=auto                 # he, en, auto
TRANSCRIPTION_OUTPUT_FORMAT=lrc             # lrc, srt, txt
```

### 🌐 API Server Configuration

```bash
# API server
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# CORS
API_CORS_ORIGINS=*                          # * or comma-separated list
```

### 🖥️ Streamlit Client Configuration

```bash
# Streamlit app
STREAMLIT_TITLE=HebKaraoke
STREAMLIT_THEME=dark                        # dark or light

# API connection
STREAMLIT_API_BASE_URL=http://localhost:8000
```

### 🏗️ Project Global Configuration

```bash
# Project metadata
PROJECT_NAME=HebKaraoke
PROJECT_VERSION=1.0.0
ENVIRONMENT=development                     # development, staging, production
```

## 🚀 Usage Examples

### Using in Python Code

```python
from shared.config import config

# Access specific configuration
kafka_servers = config.kafka.bootstrap_servers
es_host = config.elasticsearch.host
storage_path = config.storage.base_path

# Check environment
if config.is_production():
    # Production settings
    pass
elif config.is_development():
    # Development settings
    pass
```

### .env File for Development

```bash
# .env - Example for local development
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Storage
STORAGE_BASE_PATH=/tmp/karaoke

# Logging
LOG_LEVEL=DEBUG

# Services
YOUTUBE_API_KEY=your-api-key-here
API_PORT=8000
STREAMLIT_API_BASE_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
```

### .env File for Production

```bash
# .env.production - Example for production
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka-cluster:9092

# Elasticsearch
ELASTICSEARCH_SCHEME=https
ELASTICSEARCH_HOST=elasticsearch-cluster
ELASTICSEARCH_PORT=443
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=secure_password_123

# Storage
STORAGE_TYPE=s3
STORAGE_S3_BUCKET=production-karaoke-files
STORAGE_S3_REGION=us-east-1

# Logging
LOG_LEVEL=INFO
LOG_ELASTICSEARCH_ENABLED=true

# Services
API_HOST=0.0.0.0
API_PORT=80
API_DEBUG=false

# Environment
ENVIRONMENT=production
```

## 🐳 Docker Compose Example

```yaml
version: '3.8'

services:
  youtube-service:
    image: hebkaraoke/youtube-service
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - ELASTICSEARCH_HOST=elasticsearch
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - STORAGE_BASE_PATH=/data
      - LOG_LEVEL=INFO
    volumes:
      - karaoke-data:/data

  audio-service:
    image: hebkaraoke/audio-service
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - ELASTICSEARCH_HOST=elasticsearch
      - AUDIO_VOCAL_REMOVAL_METHOD=spleeter
      - STORAGE_BASE_PATH=/data
    volumes:
      - karaoke-data:/data

  api-server:
    image: hebkaraoke/api-server
    environment:
      - ELASTICSEARCH_HOST=elasticsearch
      - STORAGE_BASE_PATH=/data
      - API_PORT=8000
    ports:
      - "8000:8000"
    volumes:
      - karaoke-data:/data

volumes:
  karaoke-data:
```

## 🔧 Kubernetes ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hebkaraoke-config
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka-cluster:9092"
  ELASTICSEARCH_HOST: "elasticsearch-cluster"
  ELASTICSEARCH_PORT: "9200"
  STORAGE_TYPE: "s3"
  STORAGE_S3_BUCKET: "production-karaoke"
  STORAGE_S3_REGION: "us-east-1"
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
```

## ✅ Configuration Validation

### Validation Script

```python
# check_config.py
from shared.config import config

def check_configuration():
    print("🔍 Configuration Check")
    print(f"📡 Kafka: {config.kafka.bootstrap_servers}")
    print(f"🔍 Elasticsearch: {config.elasticsearch.url}")
    print(f"💾 Storage: {config.storage.base_path}")
    print(f"🌍 Environment: {config.environment}")

    # Connection tests
    from shared.kafka import KafkaProducerAsync
    from shared.elasticsearch import elasticsearch_config

    print("\n🧪 Connection Tests:")
    try:
        producer = KafkaProducerAsync()
        print(f"✅ Kafka Producer: {producer.bootstrap_servers}")
    except Exception as e:
        print(f"❌ Kafka Error: {e}")

    try:
        es_info = elasticsearch_config.get_connection_info()
        print(f"✅ Elasticsearch: {es_info['url']}")
    except Exception as e:
        print(f"❌ Elasticsearch Error: {e}")

if __name__ == "__main__":
    check_configuration()
```

## 📊 Configuration Priority

1. **Environment variables** (highest priority)
2. **Config file** (if implemented)
3. **Default values** (lowest priority)

### Example Priority Flow:
```python
# This value is determined in this order:
# 1. KAFKA_BOOTSTRAP_SERVERS environment variable
# 2. Default value "localhost:9092"
kafka_servers = config.kafka.bootstrap_servers
```

## 🔄 Dynamic Configuration

### Runtime Configuration Changes

```python
from shared.config import config

# Read current configuration
current_log_level = config.logger.level

# For services that support dynamic config:
def update_log_level(new_level):
    import logging
    logging.getLogger().setLevel(getattr(logging, new_level.upper()))
    print(f"Log level changed to: {new_level}")
```

### Service-Specific Configuration Access

```python
from shared.config import config

# YouTube service
youtube_config = config.youtube
api_key = youtube_config.api_key
download_quality = youtube_config.download_quality

# Audio service
audio_config = config.audio
vocal_method = audio_config.vocal_removal_method
sample_rate = audio_config.sample_rate
```

## 📚 Important Notes

### 🔒 Security
- **Never** hardcode passwords in code
- Use `.env` files or secrets management
- In production, use Kubernetes secrets or AWS Parameter Store

### 🏷️ Variable Naming
- All environment variables start with service name: `KAFKA_`, `ELASTICSEARCH_`, etc.
- Use consistent names across all environments
- Names must be in English and UPPERCASE

### 🔄 Default Values
- Every variable has a sensible default for local development
- Production deployments should explicitly set all values
- Defaults are suitable for localhost development

### 🧪 Testing
- Use `check_config.py` script to verify everything is working
- Test all connections before starting services
- Each service should log its configuration on startup

### 🌍 Environment-Specific Settings

```python
# Different configurations per environment
if config.is_development():
    # Debug logging, local services
    log_level = "DEBUG"
    kafka_servers = "localhost:9092"

elif config.is_production():
    # Production logging, clustered services
    log_level = "INFO"
    kafka_servers = "kafka-cluster:9092"
```