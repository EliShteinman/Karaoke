from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config.youtube_config import (
    YOUTUBE_API_KEY,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
)
from app.models.youtube_models import SearchResponse, SearchResult
from app.config.logger import get_logger


class YouTubeSearchService:
    def __init__(self, api_key: str = YOUTUBE_API_KEY):
        self.api_key = api_key
        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=self.api_key,
        )
        self.logger = get_logger(self.__class__.__name__)

    async def search(self, query: str, max_results: int = 10) -> SearchResponse:
        self.logger.info(f"Searching YouTube for query='{query}'")

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
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]

                results.append(
                    SearchResult(
                        video_id=video_id,
                        title=snippet["title"],
                        channel=snippet["channelTitle"],
                        thumbnail=snippet["thumbnails"]["high"]["url"],
                        published_at=snippet["publishedAt"],
                    )
                )

            self.logger.info(f"Found {len(results)} results for query='{query}'")
            return SearchResponse(results=results)

        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return SearchResponse(results=[])

        except Exception as e:
            self.logger.exception(f"Unexpected error while searching YouTube: {e}")
            return SearchResponse(results=[])
