# Shared Package - HebKaraoke Project

This package contains all shared code between different services in the Hebrew Karaoke project.

## 📁 Directory Structure

```
shared/
├── kafka/          # Kafka clients (async and sync)
├── elasticsearch/  # Elasticsearch clients and document management
├── storage/        # Audio and lyrics file management
├── utils/          # Shared utilities (logger, etc.)
├── config.py       # Central configuration management
├── README.md       # English documentation
├── README_HE.md    # Hebrew documentation
├── CONFIGURATION.md # Environment variables guide (English)
└── CONFIGURATION_HE.md # Environment variables guide (Hebrew)
```

## 🎵 File Storage Usage

### Create File Manager

```python
from shared.storage import create_file_manager

# Create file manager for local volume
file_manager = create_file_manager("volume", base_path="/shared")
```

### Save Files

```python
# Save original audio
audio_path = file_manager.save_original_audio("video123", audio_bytes)

# Save vocals-removed audio
vocals_path = file_manager.save_vocals_removed_audio("video123", processed_audio)

# Save lyrics file
lyrics_path = file_manager.save_lyrics_file("video123", lrc_content)
```

### Read Files

```python
# Read audio
original_audio = file_manager.get_original_audio("video123")
vocals_removed = file_manager.get_vocals_removed_audio("video123")

# Read lyrics as text
lyrics = file_manager.get_lyrics("video123")
```

### Checks and Package Creation

```python
# Check if song is ready for karaoke
if file_manager.is_song_ready_for_karaoke("video123"):
    # Create ZIP with required files
    zip_content = file_manager.create_karaoke_package("video123")

# Get file information
info = file_manager.get_song_files_info("video123")
```

## 📡 Kafka Usage

### Producer (Send Messages)

```python
from shared.kafka import KafkaProducerAsync, KafkaProducerSync

# Async - defaults to localhost:9092
producer = KafkaProducerAsync()  # connects to localhost:9092
# Or specify custom address:
# producer = KafkaProducerAsync("my-kafka-server:9092")

await producer.start()
await producer.send_message("my-topic", {"data": "value"}, key="optional_key")
await producer.stop()

# Sync - defaults to localhost:9092
producer = KafkaProducerSync()  # connects to localhost:9092
# Or specify custom address:
# producer = KafkaProducerSync("my-kafka-server:9092")

producer.start()
producer.send_message("my-topic", {"data": "value"}, key="optional_key")
producer.stop()
```

### Consumer (Receive Messages)

```python
from shared.kafka import KafkaConsumerAsync, KafkaConsumerSync

# Async - continuous listening
consumer = KafkaConsumerAsync(["my-topic"])  # defaults to localhost:9092
# Or with custom settings:
# consumer = KafkaConsumerAsync(["my-topic"], "my-kafka:9092", "my-group")

await consumer.start()

async def handle_message(message):
    print(f"Received: {message}")
    return True

await consumer.listen_forever(handle_message)
await consumer.stop()

# Sync - get new messages
consumer = KafkaConsumerSync(["my-topic"])  # defaults to localhost:9092
consumer.start()
messages = consumer.get_new_messages(timeout_seconds=5)
consumer.stop()
```

### Send Multiple Messages

```python
# Send in parallel (async)
count = await producer.send_batch("my-topic", [msg1, msg2, msg3])

# Send sequentially (sync)
count = producer.send_batch("my-topic", [msg1, msg2, msg3])
```

## 🔍 Elasticsearch Usage

### Create Song Repository

```python
from shared.elasticsearch import get_song_repository

# Async (default)
song_repo = get_song_repository(async_mode=True)

# Sync
song_repo = get_song_repository(async_mode=False)
```

### Song Operations

```python
# Create new song
song = await song_repo.create_song(
    video_id="video123",
    title="Song Title",
    artist="Artist Name",
    channel="YouTube Channel",
    duration=180,
    thumbnail="http://...",
    search_text="search keywords"
)

# Update file path
await song_repo.update_file_path("video123", "vocals_removed", "/path/to/file")

# Update status
await song_repo.update_song_status("video123", "processing")

# Mark as failed
await song_repo.mark_song_failed("video123", "DOWNLOAD_FAILED", "Error message", "youtube_service")
```

### Search and Queries

```python
# Get songs ready for karaoke
ready_songs = await song_repo.get_ready_songs()

# Search songs by text
results = await song_repo.search_songs("rick astley", limit=10, offset=0)

# Songs by status
downloading = await song_repo.get_songs_by_status("downloading")

# Songs needing processing
need_vocals = await song_repo.get_songs_for_processing("vocals_removed")
```

### Advanced Configuration

```python
from shared.elasticsearch import elasticsearch_config, ElasticsearchFactory

# Change settings
elasticsearch_config.songs_index = "my-songs-index"

# Create custom services
es_service = ElasticsearchFactory.create_elasticsearch_service("logs", async_mode=True)
```

## 📝 Logger Usage

```python
from shared.utils import Logger

# Get logger
logger = Logger.get_logger(
    name="my-service",
    es_url="http://localhost:9200",
    index="logs",
    level=logging.INFO
)

# Write logs (sent to both console and Elasticsearch)
logger.info("Service started")
logger.error("Error during processing")
logger.debug("Debug information")
```

## ⚙️ Environment Variables

### Kafka
```bash
# No required environment variables - default address: localhost:9092
```

### Elasticsearch
```bash
ELASTICSEARCH_SCHEME=http
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=user
ELASTICSEARCH_PASSWORD=pass
ELASTICSEARCH_SONGS_INDEX=songs
ELASTICSEARCH_LOGS_INDEX=logs
```

### File Storage
```bash
# Base path for volume (default: /shared)
FILE_STORAGE_BASE_PATH=/shared
```

## 🏗️ Complete Example - Audio Processing Service

```python
import asyncio
from shared.kafka import KafkaConsumerAsync, KafkaProducerAsync
from shared.elasticsearch import get_song_repository
from shared.storage import create_file_manager
from shared.utils import Logger

async def audio_processing_service():
    # Create components
    consumer = KafkaConsumerAsync(["audio.process.requested"], group_id="audio-service")
    producer = KafkaProducerAsync()
    song_repo = get_song_repository()
    file_manager = create_file_manager()
    logger = Logger.get_logger("audio-service")

    # Start
    await consumer.start()
    await producer.start()

    async def process_audio_message(message):
        try:
            video_id = message["value"]["video_id"]
            logger.info(f"Processing audio for {video_id}")

            # Read original audio
            original_audio = file_manager.get_original_audio(video_id)

            # Process vocal removal (dummy code)
            processed_audio = remove_vocals(original_audio)

            # Save result
            path = file_manager.save_vocals_removed_audio(video_id, processed_audio)

            # Update Elasticsearch
            await song_repo.update_file_path(video_id, "vocals_removed", path)

            # Send completion message
            await producer.send_message("audio.vocals_processed", {
                "video_id": video_id,
                "status": "vocals_processed",
                "path": path
            })

            return True

        except Exception as e:
            logger.error(f"Failed to process audio: {e}")
            await song_repo.mark_song_failed(video_id, "AUDIO_PROCESSING_FAILED", str(e), "audio-service")
            return False

    # Listen for messages
    await consumer.listen_forever(process_audio_message)

# Run
if __name__ == "__main__":
    asyncio.run(audio_processing_service())
```

## 📚 Important Notes

- **Async vs Sync**: Default is async. Use sync only when necessary
- **Elasticsearch Mapping**: Song mapping is fixed and optimized for the Karaoke project
- **Connection Management**: Always call `start()` and `stop()` for Kafka clients
- **Error Handling**: Use `mark_song_failed()` to report errors
- **Logger**: Logger automatically sends to both console and Elasticsearch

## 🎯 Quick Reference

### Import Patterns
```python
# Storage
from shared.storage import create_file_manager, KaraokeFileManager

# Kafka
from shared.kafka import KafkaProducerAsync, KafkaConsumerSync

# Elasticsearch
from shared.elasticsearch import get_song_repository, elasticsearch_config

# Utils
from shared.utils import Logger

# Configuration
from shared.config import config
```

### Common Workflows

**1. Download and Process Song:**
```python
# 1. Create song document
await song_repo.create_song(video_id, title, artist)

# 2. Save original audio
file_manager.save_original_audio(video_id, audio_bytes)

# 3. Update file path
await song_repo.update_file_path(video_id, "original", path)

# 4. Send for processing
await producer.send_message("audio.process.requested", {"video_id": video_id})
```

**2. Check Song Readiness:**
```python
# Method 1: File manager
if file_manager.is_song_ready_for_karaoke(video_id):
    zip_content = file_manager.create_karaoke_package(video_id)

# Method 2: Repository
ready_songs = await song_repo.get_ready_songs()
```

**3. Error Handling:**
```python
try:
    # Process song
    process_song(video_id)
except Exception as e:
    await song_repo.mark_song_failed(
        video_id, "PROCESSING_ERROR", str(e), "my-service"
    )
    logger.error(f"Song processing failed: {e}")
```