"""
שירות הורדה מיוטיוב - FastAPI App
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

app = FastAPI(title="HebKaraoke Downloader Service", version="1.0.0")


class DownloadRequest(BaseModel):
    youtube_url: str
    song_id: str


class DownloadResponse(BaseModel):
    job_id: str
    status: str
    message: str


@app.post("/download", response_model=DownloadResponse)
async def download_song(request: DownloadRequest) -> DownloadResponse:
    """
    הורדת שיר מיוטיוב והמרה לאודיו

    Args:
        request: בקשת הורדה

    Returns:
        תגובה עם פרטי העבודה
    """
    # TODO: מפתח A - כתוב את הלוגיקה כאן
    pass


@app.get("/status/{job_id}")
async def get_download_status(job_id: str) -> Dict[str, Any]:
    """
    קבלת סטטוס הורדה

    Args:
        job_id: מזהה העבודה

    Returns:
        סטטוס ההורדה
    """
    # TODO: מפתח A - כתוב את הלוגיקה כאן
    pass


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    בדיקת בריאות השירות

    Returns:
        סטטוס השירות
    """
    return {"status": "healthy", "service": "downloader"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)