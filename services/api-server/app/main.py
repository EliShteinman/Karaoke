from fastapi import FastAPI
from .core.config import settings
from .api.routers import songs, youtube
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
# All routes from the songs router will be prefixed with /api/v1
app.include_router(songs.router, prefix=settings.API_V1_STR, tags=["Songs"])
app.include_router(youtube.router, prefix=settings.API_V1_STR, tags=["YouTube"])

@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check endpoint to confirm the server is running."""
    logger.info("Health check endpoint was called.")
    return {"status": "ok"}

logger.info("Routers included, application is ready.")
