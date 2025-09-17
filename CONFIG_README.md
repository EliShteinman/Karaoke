# Configuration Guide - HebKaraoke Project

## ⚠️ Important to Understand!

The file `/config.py` is a **template containing all environment variables that shared tools require** - not an actual configuration file!

### What this file contains:
- ✅ **All variables that shared directory requires** for each service
- ✅ **Detailed documentation** of each variable and what it does
- ✅ **Template for mandatory copying** for each service when separated
- ❌ **NOT** a file that everyone uses together

## 🔧 How Configuration Works

**Each service must create its own configuration file and copy all relevant variables!**

### Key Principles:
1. **Mandatory copying**: Each service must copy all variables that shared directory requires from it
2. **Complete independence**: Each service creates its own configuration file
3. **Base + additions**: Variables from template are mandatory base, service can add internal variables
4. **No choice**: Cannot skip variables that shared directory requires

## 🚀 How Each Service Uses Configuration

### During development phase (all services together):
```python
# In every service - import from central file
from config import config

class YouTubeService:
    def __init__(self):
        self.service_config = config.youtube_service
```

### During deployment phase (each service in separate container):
```python
# Each service creates its own config.py file
# services/youtube-service/config.py
import os

class Config:
    def __init__(self):
        # 🔴 Mandatory - all variables that shared directory requires
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")

        # 🟢 Additions - internal service variables
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is required for YouTube functionality")

# Create configuration instance
config = Config()
```

## ⚙️ Mandatory Tool Variables by Service

Based on architecture guidelines and shared directory:

### API Server
**Uses tools:** Elasticsearch (read-only)

**🔴 Mandatory variables (required by shared tools):**
```bash
# Server settings
API_HOST=0.0.0.0                               # Server IP address
API_PORT=8000                                  # Server port
API_DEBUG=false                                # Debug mode
API_CORS_ORIGINS=*                             # Allowed CORS origins

# Elasticsearch connection - required by shared/elasticsearch tools
ELASTICSEARCH_HOST=localhost                    # Elasticsearch server address
ELASTICSEARCH_PORT=9200                         # Elasticsearch port
ELASTICSEARCH_SCHEME=http                       # Protocol
ELASTICSEARCH_USERNAME=                         # Username (if auth required)
ELASTICSEARCH_PASSWORD=                         # Password (if auth required)
```

### YouTube Service
**Uses tools:** Kafka, Elasticsearch, Storage

**🔴 Mandatory variables (required by shared tools):**
```bash
# Kafka connection - required by shared/kafka tools
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # Kafka servers list
KAFKA_CONSUMER_GROUP_YOUTUBE=youtube-service   # Consumer group
KAFKA_TOPIC_DOWNLOAD_REQUESTED=song.download.requested  # Request topic
KAFKA_TOPIC_SONG_DOWNLOADED=song.downloaded    # Completion topic

# Elasticsearch connection - required by shared/elasticsearch tools
ELASTICSEARCH_HOST=localhost                    # Elasticsearch server address
ELASTICSEARCH_PORT=9200                         # Elasticsearch port
ELASTICSEARCH_SCHEME=http                       # Protocol
ELASTICSEARCH_USERNAME=                         # Username (if auth required)
ELASTICSEARCH_PASSWORD=                         # Password (if auth required)
ELASTICSEARCH_SONGS_INDEX=songs                # Songs index

# File storage - required by shared/storage tools
STORAGE_BASE_PATH=/shared                       # Base directory for files
```

**🟢 Internal service variables (additions):**
```bash
# YouTube service specific additions
YOUTUBE_API_KEY=your_api_key                    # YouTube API key
YOUTUBE_MAX_RESULTS=10                          # Search results count
YOUTUBE_DOWNLOAD_QUALITY=bestaudio             # Download quality
YOUTUBE_DOWNLOAD_FORMAT=wav                    # File format
```

### Audio Processing Service
**Uses tools:** Kafka, Elasticsearch, Storage

**🔴 Mandatory variables (required by shared tools):**
```bash
# Kafka connection - required by shared/kafka tools
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # Kafka servers list
KAFKA_CONSUMER_GROUP_AUDIO=audio-service       # Consumer group
KAFKA_TOPIC_AUDIO_PROCESS_REQUESTED=audio.process.requested  # Request topic
KAFKA_TOPIC_VOCALS_PROCESSED=audio.vocals_processed  # Completion topic

# Elasticsearch connection - required by shared/elasticsearch tools
ELASTICSEARCH_HOST=localhost                    # Elasticsearch server address
ELASTICSEARCH_PORT=9200                         # Elasticsearch port
ELASTICSEARCH_SCHEME=http                       # Protocol
ELASTICSEARCH_USERNAME=                         # Username (if auth required)
ELASTICSEARCH_PASSWORD=                         # Password (if auth required)
ELASTICSEARCH_SONGS_INDEX=songs                # Songs index

# File storage - required by shared/storage tools
STORAGE_BASE_PATH=/shared                       # Base directory for files
```

**🟢 Internal service variables (additions):**
```bash
# Audio processing specific additions
AUDIO_VOCAL_REMOVAL_METHOD=spleeter            # Vocal removal method
AUDIO_OUTPUT_FORMAT=wav                        # Output format
AUDIO_SAMPLE_RATE=44100                        # Sample rate
AUDIO_BITRATE=128k                             # Bitrate quality
```

### Transcription Service
**Uses tools:** Kafka, Elasticsearch, Storage

**🔴 Mandatory variables (required by shared tools):**
```bash
# Kafka connection - required by shared/kafka tools
KAFKA_BOOTSTRAP_SERVERS=localhost:9092         # Kafka servers list
KAFKA_CONSUMER_GROUP_TRANSCRIPTION=transcription-service  # Consumer group
KAFKA_TOPIC_TRANSCRIPTION_REQUESTED=transcription.process.requested  # Request topic
KAFKA_TOPIC_TRANSCRIPTION_DONE=transcription.done  # Completion topic

# Elasticsearch connection - required by shared/elasticsearch tools
ELASTICSEARCH_HOST=localhost                    # Elasticsearch server address
ELASTICSEARCH_PORT=9200                         # Elasticsearch port
ELASTICSEARCH_SCHEME=http                       # Protocol
ELASTICSEARCH_USERNAME=                         # Username (if auth required)
ELASTICSEARCH_PASSWORD=                         # Password (if auth required)
ELASTICSEARCH_SONGS_INDEX=songs                # Songs index

# File storage - required by shared/storage tools
STORAGE_BASE_PATH=/shared                       # Base directory for files
```

**🟢 Internal service variables (additions):**
```bash
# Transcription specific additions
TRANSCRIPTION_MODEL_NAME=whisper-base          # Recognition model
TRANSCRIPTION_LANGUAGE=auto                    # Recognition language
TRANSCRIPTION_OUTPUT_FORMAT=lrc                # Output format
```

### Streamlit Client
**Uses tools:** HTTP connection to API Server

**🔴 Mandatory variables (required by shared tools):**
```bash
# API Server connection - required by shared/http tools
STREAMLIT_API_BASE_URL=http://localhost:8000   # API server address
```

**🟢 Internal service variables (additions):**
```bash
# Interface specific additions
STREAMLIT_TITLE=HebKaraoke                     # Application title
STREAMLIT_THEME=dark                           # Theme setting
```

## 📋 Instructions for Creating Service Configuration File

### 🚨 Mandatory for every service!

When deploying each service in separate containers, **must** create separate `config.py` file for each service.

### Step 1: Create the file
```bash
# Create configuration file in service directory
touch services/youtube-service/config.py
```

### Step 2: Mandatory copying of shared variables
**Copy all relevant variables from `/config.py` exactly as they are:**

For example, for YouTube service:

```python
# services/youtube-service/config.py
import os

class Config:
    def __init__(self):
        # 🔴 Mandatory - exact copy from template
        # All variables that shared directory requires:

        # Kafka configuration
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_consumer_group = os.getenv("KAFKA_CONSUMER_GROUP_YOUTUBE", "youtube-service")
        self.kafka_topic_download_requested = os.getenv("KAFKA_TOPIC_DOWNLOAD_REQUESTED", "song.download.requested")
        self.kafka_topic_song_downloaded = os.getenv("KAFKA_TOPIC_SONG_DOWNLOADED", "song.downloaded")

        # Elasticsearch configuration
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_scheme = os.getenv("ELASTICSEARCH_SCHEME", "http")
        self.elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME")
        self.elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")
        self.elasticsearch_songs_index = os.getenv("ELASTICSEARCH_SONGS_INDEX", "songs")

        # Storage configuration
        self.storage_base_path = os.getenv("STORAGE_BASE_PATH", "/shared")

        # 🟢 Additions - internal service variables
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")

        self.max_results = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))
        self.download_quality = os.getenv("YOUTUBE_DOWNLOAD_QUALITY", "bestaudio")
        self.download_format = os.getenv("YOUTUBE_DOWNLOAD_FORMAT", "wav")

# Create configuration instance
config = Config()
```

### ✅ Checklist for each service:

1. **Copy all mandatory variables** from template in `/config.py` - those that shared directory requires
2. **Cannot skip any variable** that shared directory needs
3. **Add internal variables** of the service as needed (API keys, specific settings)
4. **Ensure all variables are documented** with explanation of what they do
5. **Create `config` instance** at end of file

### 🟢 Adding Internal Variables - Guide

**Variables from template are mandatory base!** On this base, each service can add its internal variables.

#### Examples of internal variables:

**YouTube Service:**
```python
# Internal variables specific to YouTube
self.api_key = os.getenv("YOUTUBE_API_KEY")  # API key
self.max_results = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))  # Results count
self.timeout = int(os.getenv("YOUTUBE_TIMEOUT", "30"))  # Timeout
```

**Audio Service:**
```python
# Internal variables specific to audio processing
self.threads = int(os.getenv("AUDIO_THREADS", "4"))  # Thread count
self.temp_dir = os.getenv("AUDIO_TEMP_DIR", "/tmp")  # Temp directory
```

#### Principles for adding internal variables:

1. **Always on mandatory base** - first copy variables that shared directory requires
2. **Service prefix** (YOUTUBE_, AUDIO_, etc.)
3. **Reasonable default**
4. **Document what variable does**

### 🎯 Benefits of this approach:
1. **Shared directory works** - all tools get variables they need
2. **Complete independence** - each container sees only what it needs
3. **Flexibility** - each service can add internal variables
4. **Security** - no exposure to other services' variables
5. **Easy maintenance** - change in shared directory requires updating template only
