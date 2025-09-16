# Shared Package - HebKaraoke Project

This package contains shared infrastructure tools and project-specific business logic for the Hebrew Karaoke project.

## 🏗️ New Architecture (After Refactoring)

The shared library has been reorganized with proper separation of concerns:

### 📁 Directory Structure

```
shared/
├── kafka/          # Generic Kafka clients (infrastructure layer)
├── elasticsearch/  # Generic Elasticsearch services (infrastructure layer)
├── storage/        # Generic file storage tools (infrastructure layer)
├── utils/          # Generic utilities (infrastructure layer)
├── repositories/   # Project-specific business logic (SongRepository)
├── README.md       # This documentation
└── README_HE.md    # Hebrew documentation
```

## 🎵 File Storage Usage (Generic Infrastructure)

The file storage system supports different storage types: Docker Volume and local computer directory.

### Create File Manager - Different Examples

#### Docker Volume (for development and production environments)
```python
from shared.storage import create_file_manager

# Create file manager with Docker Volume
file_manager = create_file_manager("volume", base_path="/shared")

# Example with custom path
file_manager = create_file_manager("volume", base_path="/app/data")
```

#### Local Computer Directory (for local development)
```python
from shared.storage import create_file_manager

# Local directory in user's home
file_manager = create_file_manager("local", base_path="/home/user/karaoke_files")

# Directory on Windows computer
file_manager = create_file_manager("local", base_path="C:\\karaoke_files")

# Directory on Mac computer
file_manager = create_file_manager("local", base_path="/Users/username/Documents/karaoke")
```

### Save and Read Files - Practical Examples

#### Complete Example - Working with Audio Files
```python
from shared.storage import create_file_manager

def audio_processing_example():
    # Create file manager
    file_manager = create_file_manager("volume", base_path="/shared")

    video_id = "ABC123XYZ"

    # Mock data
    audio_data = b"binary_audio_data_here"  # Binary audio data

    # Save original audio
    try:
        audio_path = file_manager.save_original_audio(video_id, audio_data)
        print(f"Audio saved at: {audio_path}")

        # Check that file was saved successfully
        saved_audio = file_manager.get_original_audio(video_id)
        if saved_audio:
            print("Audio loaded successfully from storage")

        # Process audio (mock)
        processed_audio = saved_audio + b"_processed"

        # Save processed audio
        vocals_path = file_manager.save_vocals_removed_audio(video_id, processed_audio)
        print(f"Processed audio saved at: {vocals_path}")

    except Exception as e:
        print(f"Error processing audio: {e}")

# Run
if __name__ == "__main__":
    audio_processing_example()
```

#### Example - Working with Lyrics Files
```python
from shared.storage import create_file_manager

def lyrics_example():
    file_manager = create_file_manager("local", base_path="/tmp/karaoke")

    video_id = "XYZ789"

    # Save lyrics
    lyrics_content = """[00:12.00]First line
[00:15.50]Second line
[00:20.00]Third line"""

    lyrics_path = file_manager.save_lyrics_file(video_id, lyrics_content)
    print(f"Lyrics saved at: {lyrics_path}")

    # Read lyrics
    saved_lyrics = file_manager.get_lyrics(video_id)
    if saved_lyrics:
        print("Lyrics content:")
        print(saved_lyrics)

if __name__ == "__main__":
    lyrics_example()
```

#### Example - Karaoke Readiness Check
```python
from shared.storage import create_file_manager

def karaoke_readiness_check():
    file_manager = create_file_manager("volume", base_path="/shared")

    video_id = "READY123"

    # Check if song is ready for karaoke
    if file_manager.is_song_ready_for_karaoke(video_id):
        print("Song is ready for karaoke!")

        # Create karaoke package
        karaoke_zip = file_manager.create_karaoke_package(video_id)
        print(f"Karaoke package created: {len(karaoke_zip)} bytes")

        # Song files info
        files_info = file_manager.get_song_files_info(video_id)
        print("Files info:")
        for file_type, exists in files_info.items():
            status = "✅ Exists" if exists else "❌ Missing"
            print(f"  {file_type}: {status}")
    else:
        print("Song is not yet ready for karaoke")

if __name__ == "__main__":
    karaoke_readiness_check()
```

## 📡 Kafka Usage (Generic Infrastructure)

### Producer (Send Messages)

#### Async
```python
import asyncio
from shared.kafka import KafkaProducerAsync

async def producer_example():
    producer = KafkaProducerAsync(bootstrap_servers="localhost:9092")

    await producer.start()

    # Send message
    await producer.send_message("my-topic", {"data": "value"}, key="optional_key")

    await producer.stop()

# Run
if __name__ == "__main__":
    asyncio.run(producer_example())
```

#### Sync
```python
from shared.kafka import KafkaProducerSync

def sync_producer_example():
    producer = KafkaProducerSync(bootstrap_servers="localhost:9092")

    producer.start()

    # Send message
    producer.send_message("my-topic", {"data": "value"}, key="optional_key")

    producer.stop()

if __name__ == "__main__":
    sync_producer_example()
```

### Consumer (Receive Messages)

#### Async
```python
import asyncio
from shared.kafka import KafkaConsumerAsync

async def consumer_example():
    consumer = KafkaConsumerAsync(
        topics=["my-topic"],
        bootstrap_servers="localhost:9092",
        group_id="my-group"
    )

    await consumer.start()

    async def handle_message(message):
        print(f"Received: {message}")
        return True

    # Listen for messages (runs forever)
    await consumer.listen_forever(handle_message)

if __name__ == "__main__":
    asyncio.run(consumer_example())
```

#### Sync
```python
from shared.kafka import KafkaConsumerSync

def sync_consumer_example():
    consumer = KafkaConsumerSync(
        topics=["my-topic"],
        bootstrap_servers="localhost:9092",
        group_id="my-group"
    )

    consumer.start()

    def handle_message(message):
        print(f"Received: {message}")
        return True

    # Listen for messages
    consumer.listen_forever(handle_message)

if __name__ == "__main__":
    sync_consumer_example()
```

## 🔍 Elasticsearch Usage (Infrastructure + Business Logic)

### Using Generic Elasticsearch Factory

```python
from shared.elasticsearch import ElasticsearchFactory

# Create service with explicit parameters
es_service = ElasticsearchFactory.create_elasticsearch_service(
    index_name="logs",
    elasticsearch_host="localhost",
    elasticsearch_port=9200,
    elasticsearch_scheme="http",
    async_mode=True
)

# Service with authentication
es_service_auth = ElasticsearchFactory.create_elasticsearch_service(
    index_name="secure_logs",
    elasticsearch_host="es-cluster.example.com",
    elasticsearch_port=9200,
    elasticsearch_scheme="https",
    elasticsearch_username="user",
    elasticsearch_password="password",
    async_mode=True
)
```

### Using Project-Specific Repositories

```python
from shared.repositories import RepositoryFactory

# Create song repository with explicit parameters
song_repo = RepositoryFactory.create_song_repository_from_params(
    elasticsearch_host="localhost",
    elasticsearch_port=9200,
    elasticsearch_scheme="http",
    songs_index="songs",
    async_mode=True
)

# With authentication
secure_song_repo = RepositoryFactory.create_song_repository_from_params(
    elasticsearch_host="secure-es.example.com",
    elasticsearch_port=9200,
    elasticsearch_scheme="https",
    elasticsearch_username="app_user",
    elasticsearch_password="app_password",
    songs_index="production_songs",
    async_mode=True
)
```

### Song Operations (Business Logic)

```python
import asyncio
from shared.repositories import RepositoryFactory

async def song_operations_example():
    # Create repository
    song_repo = RepositoryFactory.create_song_repository_from_params(
        elasticsearch_host="localhost",
        elasticsearch_port=9200,
        songs_index="songs",
        async_mode=True
    )

    # Create new song
    song = await song_repo.create_song(
        video_id="video123",
        title="Song Title",
        artist="Artist Name",
        channel="YouTube Channel",
        duration=180,
        thumbnail="http://example.com/thumb.jpg",
        search_text="search keywords"
    )

    # Update operations
    await song_repo.update_file_path("video123", "vocals_removed", "/path/to/file")
    await song_repo.update_song_status("video123", "processing")

    # Search and queries
    ready_songs = await song_repo.get_ready_songs()
    results = await song_repo.search_songs("rick astley", limit=10, offset=0)
    downloading = await song_repo.get_songs_by_status("downloading")

if __name__ == "__main__":
    asyncio.run(song_operations_example())
```

## 📝 Logger Usage (Generic Infrastructure)

```python
import logging
from shared.utils import Logger

def logger_example():
    # Get logger with explicit parameters
    logger = Logger.get_logger(
        name="my-service",
        es_url="http://localhost:9200",
        index="logs",
        level=logging.INFO
    )

    # Logger with secure Elasticsearch
    secure_logger = Logger.get_logger(
        name="secure-service",
        es_url="https://user:password@es-cluster.example.com:9200",
        index="secure_logs",
        level=logging.DEBUG
    )

    # Write logs
    logger.info("Service started")
    logger.error("Error during processing")

    # Local-only logger (no Elasticsearch)
    local_logger = Logger.get_logger(name="local-service")
    local_logger.info("Local log only")

if __name__ == "__main__":
    logger_example()
```

## 🏗️ Complete Example - Audio Processing Service

```python
import asyncio
import logging
from shared.kafka import KafkaConsumerAsync, KafkaProducerAsync
from shared.repositories import RepositoryFactory
from shared.storage import create_file_manager
from shared.utils import Logger

async def complete_audio_service_example():
    # Set parameters (usually would come from configuration)
    kafka_servers = "localhost:9092"
    es_host = "localhost"
    es_port = 9200
    storage_path = "/shared"

    # Create components
    consumer = KafkaConsumerAsync(
        topics=["audio.process.requested"],
        bootstrap_servers=kafka_servers,
        group_id="audio-service"
    )

    producer = KafkaProducerAsync(bootstrap_servers=kafka_servers)

    song_repo = RepositoryFactory.create_song_repository_from_params(
        elasticsearch_host=es_host,
        elasticsearch_port=es_port,
        songs_index="songs",
        async_mode=True
    )

    file_manager = create_file_manager("volume", base_path=storage_path)
    logger = Logger.get_logger("audio-service")

    # Start services
    await consumer.start()
    await producer.start()

    async def process_audio_message(message):
        try:
            video_id = message["value"]["video_id"]
            logger.info(f"Processing audio for {video_id}")

            # Read original audio
            original_audio = file_manager.get_original_audio(video_id)
            if not original_audio:
                logger.error(f"No original audio found for {video_id}")
                return False

            # Process vocal removal (mock)
            processed_audio = original_audio + b"_vocals_removed"

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

            logger.info(f"Audio processing completed for {video_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to process audio: {e}")
            await song_repo.mark_song_failed(video_id, "AUDIO_PROCESSING_FAILED", str(e), "audio-service")
            return False

    # Listen for messages
    logger.info("Audio processing service started")
    await consumer.listen_forever(process_audio_message)

# Run
if __name__ == "__main__":
    asyncio.run(complete_audio_service_example())
```

## 📚 Important Notes

- **Independence**: Each tool works independently with explicit parameters
- **Flexibility**: Tools can be used with any configuration system
- **Isolation**: Infrastructure tools don't depend on specific configuration
- **Reusability**: Tools can be used in different projects

## 🎯 Quick Reference

### Import Patterns
```python
# Generic Infrastructure Tools
from shared.storage import create_file_manager
from shared.kafka import KafkaProducerAsync, KafkaConsumerSync
from shared.elasticsearch import ElasticsearchFactory
from shared.utils import Logger

# Project-Specific Business Logic
from shared.repositories import RepositoryFactory
```

### Usage Principles

1. **Explicit Parameters**: Each tool receives its parameters explicitly
2. **No Configuration Dependencies**: Tools don't know where parameters come from
3. **Flexibility**: Can be used with any configuration system or none at all
4. **Independence**: Each tool works without dependence on specific project