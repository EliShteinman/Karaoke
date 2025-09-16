from fastapi import FastAPI
from app.models.youtube_models import (
    SearchRequest, SearchResponse,
    DownloadRequest, DownloadResponse
)
from app.services.youtube_search import YouTubeSearchService
from app.services.youtube_download import YouTubeDownloadService




app = FastAPI(title="YouTube Service")

youtube_service = YouTubeSearchService()
youtube_download_service = YouTubeDownloadService()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/search", response_model=SearchResponse)
async def search_songs(payload: SearchRequest):
    return await youtube_service.search(payload.query)

@app.post("/download", response_model=DownloadResponse)
async def download_song(payload: DownloadRequest):
    return await youtube_download_service.download(payload.video_id)
