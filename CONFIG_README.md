# Configuration Guide - HebKaraoke Project

Complete guide for the centralized configuration system in `/config.py`.

## 🔧 How Configuration Works

The configuration system is **centralized and modular**. Each service has a self-contained configuration class that explicitly defines ALL environment variables it needs.

### Key Principles:
1. **Self-Contained**: Each service sees ALL parameters it needs in one place
2. **Explicit**: No hidden dependencies or shared global configuration
3. **Smart Defaults**: Safe defaults for development, required validation for critical settings
4. **Duplication by Design**: Even if services use the same infrastructure, each defines its own parameters for clarity

## 📋 Service Configuration Classes

### How Each Service Imports Configuration

```python
# In every service - import the central configuration
from config import config

# YouTube Service
class YouTubeService:
    def __init__(self):
        # The service receives only its own configuration
        self.service_config = config.youtube_service

        # All parameters are available in its configuration
        self.api_key = self.service_config.api_key
        self.kafka_servers = self.service_config.kafka_bootstrap_servers
        self.es_host = self.service_config.elasticsearch_host

# Audio Service
class AudioService:
    def __init__(self):
        # The service receives only its own configuration
        self.service_config = config.audio_service

        # All parameters are available in its configuration
        self.kafka_servers = self.service_config.kafka_bootstrap_servers
        self.es_host = self.service_config.elasticsearch_host
        self.storage_path = self.service_config.storage_base_path

# API Server
class APIServer:
    def __init__(self):
        # The service receives only its own configuration
        self.service_config = config.api_server

        # All parameters are available in its configuration
        self.host = self.service_config.host
        self.port = self.service_config.port
        self.kafka_servers = self.service_config.kafka_bootstrap_servers
```

## ⚙️ Environment Variables by Service

### YouTube Service (`config.youtube_service`)

**Service-Specific Settings:**
```bash
YOUTUBE_API_KEY=your_api_key                    # REQUIRED - no default
YOUTUBE_MAX_RESULTS=10                          # optional
YOUTUBE_DOWNLOAD_QUALITY=bestaudio             # optional
YOUTUBE_DOWNLOAD_FORMAT=mp3                    # optional
```

**Infrastructure Dependencies (explicitly defined for this service):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # optional - has default
KAFKA_CONSUMER_GROUP_YOUTUBE=youtube-service   # optional - has default
KAFKA_TOPIC_DOWNLOAD_REQUESTED=song.download.requested  # optional - has default
KAFKA_TOPIC_SONG_DOWNLOADED=song.downloaded    # optional - has default

ELASTICSEARCH_HOST=localhost                    # optional - has default
ELASTICSEARCH_PORT=9200                         # optional - has default
ELASTICSEARCH_SCHEME=http                       # optional - has default
ELASTICSEARCH_USERNAME=                         # optional - no default (auth)
ELASTICSEARCH_PASSWORD=                         # optional - no default (auth)
ELASTICSEARCH_SONGS_INDEX=songs                # optional - has default

STORAGE_BASE_PATH=/shared                       # optional - has default
```

### Audio Service (`config.audio_service`)

**Service-Specific Settings:**
```bash
AUDIO_VOCAL_REMOVAL_METHOD=spleeter            # optional - has default
AUDIO_OUTPUT_FORMAT=mp3                        # optional - has default
AUDIO_SAMPLE_RATE=44100                        # optional - has default
AUDIO_BITRATE=128k                             # optional - has default
```

**Infrastructure Dependencies (explicitly defined for this service):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # optional - has default
KAFKA_CONSUMER_GROUP_AUDIO=audio-service       # optional - has default
KAFKA_TOPIC_AUDIO_PROCESS_REQUESTED=audio.process.requested  # optional - has default
KAFKA_TOPIC_VOCALS_PROCESSED=audio.vocals_processed  # optional - has default

ELASTICSEARCH_HOST=localhost                    # optional - has default
ELASTICSEARCH_PORT=9200                         # optional - has default
ELASTICSEARCH_SCHEME=http                       # optional - has default
ELASTICSEARCH_USERNAME=                         # optional - no default (auth)
ELASTICSEARCH_PASSWORD=                         # optional - no default (auth)
ELASTICSEARCH_SONGS_INDEX=songs                # optional - has default

STORAGE_BASE_PATH=/shared                       # optional - has default
```

### API Server (`config.api_server`)

**Service-Specific Settings:**
```bash
API_HOST=0.0.0.0                               # optional - has default
API_PORT=8000                                  # optional - has default
API_DEBUG=false                                # optional - has default
API_CORS_ORIGINS=*                             # optional - has default
```

**Infrastructure Dependencies (explicitly defined for this service):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # optional - has default

ELASTICSEARCH_HOST=localhost                    # optional - has default
ELASTICSEARCH_PORT=9200                         # optional - has default
ELASTICSEARCH_SCHEME=http                       # optional - has default
ELASTICSEARCH_USERNAME=                         # optional - no default (auth)
ELASTICSEARCH_PASSWORD=                         # optional - no default (auth)
```

### Transcription Service (`config.transcription_service`)

**Service-Specific Settings:**
```bash
TRANSCRIPTION_MODEL_NAME=whisper-base          # optional - has default
TRANSCRIPTION_LANGUAGE=auto                    # optional - has default
TRANSCRIPTION_OUTPUT_FORMAT=lrc                # optional - has default
```

**Infrastructure Dependencies (explicitly defined for this service):**
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # optional - has default
KAFKA_CONSUMER_GROUP_TRANSCRIPTION=transcription-service  # optional - has default
KAFKA_TOPIC_TRANSCRIPTION_REQUESTED=transcription.process.requested  # optional - has default
KAFKA_TOPIC_TRANSCRIPTION_DONE=transcription.done  # optional - has default

ELASTICSEARCH_HOST=localhost                    # optional - has default
ELASTICSEARCH_PORT=9200                         # optional - has default
ELASTICSEARCH_SCHEME=http                       # optional - has default
ELASTICSEARCH_USERNAME=                         # optional - no default (auth)
ELASTICSEARCH_PASSWORD=                         # optional - no default (auth)
ELASTICSEARCH_SONGS_INDEX=songs                # optional - has default

STORAGE_BASE_PATH=/shared                       # optional - has default
```

### Streamlit Client (`config.streamlit_client`)

**Service-Specific Settings:**
```bash
STREAMLIT_TITLE=HebKaraoke                     # optional - has default
STREAMLIT_THEME=dark                           # optional - has default
STREAMLIT_API_BASE_URL=http://localhost:8000   # optional - has default
```

## 🏗️ Global Project Settings

**Project Metadata:**
```bash
PROJECT_NAME=HebKaraoke                        # optional - has default
PROJECT_VERSION=1.0.0                         # optional - has default
ENVIRONMENT=development                        # optional - has default (development/production)
```

## 🔐 Configuration Security

### Required vs Optional Variables

**REQUIRED** (will throw error if missing):
- `YOUTUBE_API_KEY` - Critical for YouTube service functionality

**OPTIONAL** (have safe defaults):
- All infrastructure settings (hosts, ports, etc.)
- All service-specific settings

### Smart Defaults Strategy

- **Infrastructure Settings**: Default to localhost development values
- **Critical API Keys**: No defaults - must be explicitly provided
- **Service Settings**: Sensible defaults for typical usage

### Environment-Specific Configuration

```python
from config import config

# Check environment
if config.is_production():
    # Production-specific logic
    pass
elif config.is_development():
    # Development-specific logic
    pass
```

## 📚 Configuration Examples

### Development Environment (.env)
```bash
# Only required variables
YOUTUBE_API_KEY=your_actual_api_key

# All others use defaults for local development
```

### Production Environment (.env)
```bash
# Required
YOUTUBE_API_KEY=your_production_api_key

# Infrastructure overrides
KAFKA_BOOTSTRAP_SERVERS=kafka-cluster:9092
ELASTICSEARCH_HOST=elastic-cluster
ELASTICSEARCH_USERNAME=production_user
ELASTICSEARCH_PASSWORD=production_password
STORAGE_BASE_PATH=/production/shared

# Environment
ENVIRONMENT=production
```

### Docker Compose Environment
```bash
# Service-specific ports
API_PORT=8080
STREAMLIT_API_BASE_URL=http://api-server:8080

# Cluster addresses
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ELASTICSEARCH_HOST=elasticsearch
```

## 🎯 Best Practices

1. **Service Isolation**: Each service only accesses `config.{service_name}`
2. **Explicit Parameters**: Pass configuration explicitly to shared tools
3. **Environment Files**: Use `.env` files for environment-specific settings
4. **Security**: Never commit API keys or passwords to version control
5. **Documentation**: Update this guide when adding new configuration options

## 🚀 Usage in Services

```python
# services/youtube-service/main.py
from config import config
from shared.kafka import KafkaProducerAsync
from shared.repositories import RepositoryFactory

def main():
    # Get service configuration
    service_config = config.youtube_service

    # Create components with explicit configuration
    producer = KafkaProducerAsync(
        bootstrap_servers=service_config.kafka_bootstrap_servers
    )

    song_repo = RepositoryFactory.create_song_repository_from_config(
        service_config, async_mode=True
    )

    # Service logic here...
```

This approach ensures that each service has complete visibility into all configuration it needs while maintaining clean separation between services.