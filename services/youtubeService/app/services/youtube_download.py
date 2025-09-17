import yt_dlp
import os
import threading
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

from services.youtubeService.app.models.youtube_models import (
    DownloadResponse,
    SongDownloadedMessage,
    AudioProcessRequestMessage,
    TranscriptionRequestMessage,
    DownloadErrorMessage
)
from services.youtubeService.app.config.config import config
from shared.utils.logger import Logger
from shared.repositories.factory import RepositoryFactory
from shared.kafka.sync_client import KafkaProducerSync
from shared.storage.file_storage import create_file_manager


class YouTubeDownloadService:
    def __init__(self, base_path: str = config.SHARED_STORAGE_PATH):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize logger with proper configuration
        logger_config = config.get_logger_config()
        logger_config["name"] = "youtube_service.download"
        self.logger = Logger.get_logger(**logger_config)

        # Initialize shared services using proper configuration
        self.song_repository = RepositoryFactory.create_song_repository_from_params(
            elasticsearch_host=config.ELASTICSEARCH_HOST,
            elasticsearch_port=config.ELASTICSEARCH_PORT,
            elasticsearch_scheme=config.ELASTICSEARCH_SCHEME,
            songs_index=config.ELASTICSEARCH_INDEX,
            async_mode=False  # Use sync repository for YouTube service
        )
        self.kafka_producer = KafkaProducerSync(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
        self.file_manager = create_file_manager(storage_type="volume", base_path=str(self.base_path))

        self.logger.info("YouTubeDownloadService initialized with shared services")

    def start_download_async(
        self,
        video_id: str,
        title: str,
        channel: str,
        duration: int,
        thumbnail: str
    ) -> None:
        """
        Start the download process in background thread.
        This method validates the request and starts the download asynchronously.
        """
        self.logger.info(f"Starting async download for video_id='{video_id}'")

        # Basic validation (video_id should be non-empty)
        if not video_id or not video_id.strip():
            raise ValueError("video_id cannot be empty")

        # Start download in background thread
        download_thread = threading.Thread(
            target=self._download_workflow,
            args=(video_id, title, channel, duration, thumbnail),
            daemon=True
        )
        download_thread.start()

        self.logger.info(f"Download thread started for video_id='{video_id}'")

    def _download_workflow(
        self,
        video_id: str,
        title: str,
        channel: str,
        duration: int,
        thumbnail: str
    ) -> None:
        """
        Internal method to run the complete download workflow in background.
        This is called by the background thread.
        """
        self.logger.info(f"Starting background download workflow for video_id='{video_id}'")

        try:
            # Step 1: Create initial Elasticsearch document
            self._create_initial_document(video_id, title, channel, duration, thumbnail)

            # Step 2: Download the file
            file_path = self._download_file(video_id)

            # Step 3: Update Elasticsearch with file path and metadata
            self._update_document_after_download(video_id, file_path)

            # Step 4: Send Kafka messages
            self._send_kafka_messages(video_id, file_path, duration)

            self.logger.info(f"Background download workflow completed successfully for video_id='{video_id}'")

        except Exception as e:
            self.logger.error(f"Background download workflow failed for video_id='{video_id}': {e}")
            self._handle_download_error(video_id, str(e))

    def download(
        self,
        video_id: str,
        title: str,
        channel: str,
        duration: int,
        thumbnail: str
    ) -> DownloadResponse:
        """
        Complete download workflow:
        1. Create initial Elasticsearch document
        2. Download file using YTDLP
        3. Update Elasticsearch with file path
        4. Send 3 Kafka messages
        """
        self.logger.info(f"Starting complete download workflow for video_id='{video_id}'")

        try:
            # Step 1: Create initial Elasticsearch document
            self._create_initial_document(video_id, title, channel, duration, thumbnail)

            # Step 2: Download the file
            file_path = self._download_file(video_id)

            # Step 3: Update Elasticsearch with file path and metadata
            self._update_document_after_download(video_id, file_path)

            # Step 4: Send Kafka messages
            self._send_kafka_messages(video_id, file_path, duration)

            self.logger.info(f"Download workflow completed successfully for video_id='{video_id}'")
            return DownloadResponse(
                status="accepted",
                video_id=video_id,
                message="Song queued for processing"
            )

        except Exception as e:
            self.logger.error(f"Download workflow failed for video_id='{video_id}': {e}")
            self._handle_download_error(video_id, str(e))
            return DownloadResponse(
                status="failed",
                video_id=video_id,
                message=f"Download failed: {str(e)}"
            )

    def _create_initial_document(
        self,
        video_id: str,
        title: str,
        channel: str,
        duration: int,
        thumbnail: str
    ) -> None:
        """Create initial Elasticsearch document with status 'downloading'"""
        try:
            self.logger.info(f"Creating initial Elasticsearch document for video_id='{video_id}'")

            # Extract artist from title (simple heuristic)
            artist = self._extract_artist_from_title(title)

            self.song_repository.create_song(
                video_id=video_id,
                title=title,
                artist=artist,
                channel=channel,
                duration=duration,
                thumbnail=thumbnail,
                search_text=f"{title} {artist} {channel}".strip()
            )

            self.logger.info(f"Initial document created successfully for video_id='{video_id}'")

        except Exception as e:
            self.logger.error(f"Failed to create initial document for video_id='{video_id}': {e}")
            raise

    def _download_file(self, video_id: str) -> str:
        """Download file using YTDLP with exact schema specifications"""
        # Update status to indicate download started
        self.song_repository.update_status_field(video_id, "download", "in_progress")
        self.logger.info(f"Updated download status to 'in_progress' for video_id='{video_id}'")

        url = f"https://www.youtube.com/watch?v={video_id}"
        output_dir = self.base_path / video_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "original.mp3"

        self.logger.info(f"Starting YTDLP download for video_id='{video_id}' to '{output_file}'")

        # YTDLP options as specified in schema
        ydl_opts = {
            'format': 'bestaudio[ext=mp3]/best[ext=mp4]/best',
            'outtmpl': str(output_file.with_suffix('')),  # YTDLP will add .mp3
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': '128K',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'no_warnings': False,
            'ignoreerrors': False,
            'continuedl': True,
            'noplaylist': True,
            'writesubtitles': False,
            'writeautomaticsub': False
        }

        # Add cookies configuration if available
        self._add_cookies_to_ydl_opts(ydl_opts)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Verify file was created
            if output_file.exists():
                file_size = output_file.stat().st_size
                self.logger.info(f"Download completed: {output_file} ({file_size} bytes)")
                return str(output_file)
            else:
                raise Exception(f"Downloaded file not found at {output_file}")

        except Exception as e:
            self.logger.error(f"YTDLP download failed for video_id='{video_id}': {e}")
            raise

    def _update_document_after_download(self, video_id: str, file_path: str) -> None:
        """Update Elasticsearch document with file path and metadata"""
        try:
            self.logger.info(f"Updating Elasticsearch document after download for video_id='{video_id}'")

            # Update file path
            self.song_repository.update_file_path(video_id, "original", file_path)

            # Update status - download completed, overall status to processing
            self.song_repository.update_status_field(video_id, "download", "completed")
            self.song_repository.update_status_field(video_id, "overall", "processing")
            self.logger.info(f"Updated status: download='completed', overall='processing' for video_id='{video_id}'")

            # Get file metadata
            file_size = os.path.getsize(file_path)

            # Update metadata
            metadata = {
                "original_size": file_size,
                "download_time": 0,  # Could be tracked if needed
                "source_quality": "128kbps"
            }
            self.song_repository.update_metadata(video_id, metadata)

            self.logger.info(f"Document updated successfully for video_id='{video_id}'")

        except Exception as e:
            self.logger.error(f"Failed to update document after download for video_id='{video_id}': {e}")
            raise

    def _send_kafka_messages(self, video_id: str, file_path: str, duration: int) -> None:
        """Send 3 Kafka messages as specified in schema"""
        try:
            self.logger.info(f"Sending Kafka messages for video_id='{video_id}'")

            timestamp = datetime.now(timezone.utc).isoformat()
            file_size = os.path.getsize(file_path)

            # Message 1: song.downloaded event
            downloaded_message = SongDownloadedMessage(
                video_id=video_id,
                status="downloaded",
                metadata={
                    "duration": duration,
                    "bitrate": 128,
                    "sample_rate": 44100,
                    "file_size": file_size,
                    "format": "mp3"
                },
                timestamp=timestamp
            )

            # Message 2: audio.process.requested command (only video_id)
            audio_process_message = AudioProcessRequestMessage(
                video_id=video_id,
                action="remove_vocals"
            )

            # Message 3: transcription.process.requested command (only video_id)
            transcription_message = TranscriptionRequestMessage(
                video_id=video_id,
                action="transcribe"
            )

            # Start Kafka producer
            self.kafka_producer.start()

            # Send messages
            self.kafka_producer.send_message("song.downloaded", downloaded_message.dict())
            self.kafka_producer.send_message("audio.process.requested", audio_process_message.dict())
            self.kafka_producer.send_message("transcription.process.requested", transcription_message.dict())

            self.logger.info(f"All 3 Kafka messages sent successfully for video_id='{video_id}'")

        except Exception as e:
            self.logger.error(f"Failed to send Kafka messages for video_id='{video_id}': {e}")
            raise
        finally:
            try:
                self.kafka_producer.stop()
            except Exception as e:
                self.logger.error(f"Error stopping Kafka producer: {e}")

    def _handle_download_error(self, video_id: str, error_message: str) -> None:
        """Handle download error by updating Elasticsearch and sending error message to Kafka"""
        try:
            self.logger.info(f"Handling download error for video_id='{video_id}'")

            # Update Elasticsearch with error - specify download step failed
            self.song_repository.mark_song_failed(
                video_id=video_id,
                error_code="DOWNLOAD_FAILED",
                error_message=error_message,
                service="youtube_service",
                failed_step="download"
            )

            # Send error message to Kafka
            error_message_obj = DownloadErrorMessage(
                video_id=video_id,
                status="failed",
                error={
                    "code": "DOWNLOAD_FAILED",
                    "message": error_message,
                    "details": "",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "service": "youtube_service"
                }
            )

            try:
                self.kafka_producer.start()
                self.kafka_producer.send_message("song.download.failed", error_message_obj.dict())
                self.logger.info(f"Error message sent to Kafka for video_id='{video_id}'")
            except Exception as kafka_error:
                self.logger.error(f"Failed to send error message to Kafka: {kafka_error}")
            finally:
                try:
                    self.kafka_producer.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping Kafka producer in error handler: {e}")

        except Exception as e:
            self.logger.error(f"Failed to handle download error for video_id='{video_id}': {e}")

    def _extract_artist_from_title(self, title: str) -> str:
        """Simple heuristic to extract artist from title"""
        try:
            # Common patterns: "Artist - Song", "Artist: Song", "Song by Artist"
            if " - " in title:
                return title.split(" - ")[0].strip()
            elif ": " in title:
                return title.split(": ")[0].strip()
            elif " by " in title.lower():
                parts = title.lower().split(" by ")
                if len(parts) > 1:
                    return parts[1].strip().title()

            # If no pattern found, return empty string
            return ""
        except Exception as e:
            self.logger.error(f"Error extracting artist from title '{title}': {e}")
            return ""

    def _add_cookies_to_ydl_opts(self, ydl_opts: dict) -> None:
        """Add cookies configuration to yt-dlp options if available"""
        try:
            # Option 1: Use cookies from a file
            if config.YOUTUBE_COOKIES_FILE:
                cookies_file_path = Path(config.YOUTUBE_COOKIES_FILE)
                if cookies_file_path.exists():
                    ydl_opts['cookiefile'] = str(cookies_file_path)
                    self.logger.info(f"Using cookies from file: {cookies_file_path}")
                else:
                    self.logger.warning(f"Cookies file not found: {cookies_file_path}")

            # Option 2: Use cookies from browser (takes precedence over file)
            elif config.YOUTUBE_COOKIES_FROM_BROWSER:
                ydl_opts['cookiesfrombrowser'] = (config.YOUTUBE_COOKIES_FROM_BROWSER, None, None, None)
                self.logger.info(f"Using cookies from browser: {config.YOUTUBE_COOKIES_FROM_BROWSER}")

            else:
                self.logger.debug("No cookies configuration found - proceeding without cookies")

        except Exception as e:
            self.logger.warning(f"Failed to configure cookies: {e}. Proceeding without cookies.")