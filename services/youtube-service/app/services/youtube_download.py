import yt_dlp
from pathlib import Path
from app.models.youtube_models import DownloadResponse
from app.config.logger import get_logger


class YouTubeDownloadService:
    def __init__(self, base_path: str = "./shared/audio"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(self.__class__.__name__)

    async def download(self, video_id: str) -> DownloadResponse:
        url = f"https://www.youtube.com/watch?v={video_id}"
        output_dir = self.base_path / video_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "original.mp3"

        self.logger.info(f"Starting download for video_id={video_id}")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(output_file),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.logger.info(f"Download completed: {output_file}")
            return DownloadResponse(
                video_id=video_id,
                status="success",
                file_path=str(output_file),
            )

        except Exception as e:
            self.logger.exception(f"Download failed for video_id={video_id}: {e}")
            return DownloadResponse(
                video_id=video_id,
                status="failed",
                file_path=None,
                error=str(e),
            )
