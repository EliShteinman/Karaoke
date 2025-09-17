from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.youtubeService.app.config.config import config
from services.youtubeService.app.models.youtube_models import SearchResponse, SearchResult
from shared.utils.logger import Logger


class YouTubeSearchService:
    def __init__(self, api_key: Optional[str] = config.YOUTUBE_API_KEY):
        if not api_key:
            raise ValueError("YouTube API key is required")
        self.api_key = api_key
        self.youtube = build(
            config.YOUTUBE_API_SERVICE_NAME,
            config.YOUTUBE_API_VERSION,
            developerKey=self.api_key,
        )
        # Initialize logger with proper configuration
        logger_config = config.get_logger_config()
        logger_config["name"] = "youtube_service.search"
        self.logger = Logger.get_logger(**logger_config)
        self.logger.info("YouTubeSearchService initialized")

    def search(self, query: str, max_results: int = 10) -> SearchResponse:
        self.logger.info(f"Searching YouTube for query='{query}', max_results={max_results}")

        try:
            request = self.youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_results,
            )
            response = request.execute()

            results = []
            for item in response.get("items", []):
                video_id = "unknown"  # Initialize with default value
                try:
                    video_id = item["id"]["videoId"]
                    snippet = item["snippet"]

                    # Get additional video details
                    video_details = self.youtube.videos().list(
                        part="contentDetails,statistics",
                        id=video_id
                    ).execute()

                    duration = 0
                    view_count = 0
                    if video_details.get("items"):
                        duration_str = video_details["items"][0]["contentDetails"].get("duration", "PT0S")
                        duration = self._parse_duration(duration_str)
                        view_count = int(video_details["items"][0]["statistics"].get("viewCount", 0))

                    results.append(
                        SearchResult(
                            video_id=video_id,
                            title=snippet["title"],
                            channel=snippet["channelTitle"],
                            duration=duration,
                            thumbnail=snippet["thumbnails"]["high"]["url"],
                            published_at=snippet["publishedAt"],
                            view_count=view_count
                        )
                    )
                except Exception as item_error:
                    self.logger.error(f"Error processing search result item for video_id {video_id}: {item_error}")
                    continue

            self.logger.info(f"Found {len(results)} valid results for query='{query}'")
            return SearchResponse(results=results)

        except HttpError as e:
            self.logger.error(f"YouTube API error while searching for '{query}': {e}")
            raise Exception(f"YouTube API error: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected error while searching YouTube for '{query}': {e}")
            raise

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        try:
            import re
            pattern = r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?'
            match = re.match(pattern, duration_str)
            if match:
                hours = int(match.group('hours') or 0)
                minutes = int(match.group('minutes') or 0)
                seconds = int(match.group('seconds') or 0)
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except Exception as e:
            self.logger.error(f"Error parsing duration '{duration_str}': {e}")
            return 0
