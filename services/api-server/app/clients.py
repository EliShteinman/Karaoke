import httpx
from services.api_server.app.config import settings

# YouTube Service HTTP Client
youtube_service_client: httpx.AsyncClient = httpx.AsyncClient(
    base_url=settings.youtube_service_url,
    timeout=30.0
)
