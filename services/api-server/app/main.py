from typing import Dict
from fastapi import FastAPI
from services.api_server.app.config import settings
from services.api_server.app.api.routers import songs, youtube
from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)

# Create the main FastAPI application instance
app = FastAPI(
    title="Karaoke API Server",
    description="API Gateway for the Karaoke System. Handles client requests and orchestrates services.",
    version="1.0.0"
)

logger.info("API Server starting up...")

# Include the routers
app.include_router(songs.router, tags=["Songs"])
app.include_router(youtube.router, tags=["YouTube"])

@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Simple health check endpoint to confirm the server is running."""
    logger.info("Health check endpoint was called.")
    return {"status": "ok"}

logger.info("Routers included, application is ready.")
