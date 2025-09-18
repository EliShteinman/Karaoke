from typing import Dict
from fastapi import FastAPI
from services.apiServer.app.config import settings
from services.apiServer.app.api.routers import songs, youtube
from shared.utils.logger import Logger
from shared.elasticsearch.factory import ElasticsearchFactory
from shared.elasticsearch.song_mapping import SONGS_INDEX_MAPPING, SONGS_INDEX_SETTINGS

logger = settings.initialize_logger()

# Create the main FastAPI application instance
app = FastAPI(
    title="Karaoke API Server",
    description="API Gateway for the Karaoke System. Handles client requests and orchestrates services.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize Elasticsearch index on startup."""
    try:
        logger.info("Initializing Elasticsearch songs index...")

        # Create Elasticsearch service
        es_service = ElasticsearchFactory.create_elasticsearch_service(
            index_name=settings.elasticsearch_songs_index,
            elasticsearch_host=settings.elasticsearch_host,
            elasticsearch_port=settings.elasticsearch_port,
            elasticsearch_scheme=settings.elasticsearch_scheme,
            elasticsearch_username=settings.elasticsearch_username,
            elasticsearch_password=settings.elasticsearch_password,
            async_mode=True
        )

        # Check if index exists, create if not
        if not await es_service.is_index_exists():
            logger.info(f"Creating songs index: {settings.elasticsearch_songs_index}")
            await es_service.initialize_index(
                mapping=SONGS_INDEX_MAPPING,
                index_name=settings.elasticsearch_songs_index
            )
            logger.info("Songs index created successfully")
        else:
            logger.info(f"Songs index {settings.elasticsearch_songs_index} already exists")

    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch index: {e}")
        # Don't fail the startup, just log the error
        pass

logger.info("API Server starting up...")

# Include the routers
app.include_router(songs.router, tags=["Songs"])
app.include_router(youtube.router, tags=["YouTube"])

@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """Simple health check endpoint to confirm the server is running."""
    try:
        logger.info("Health check endpoint was called.")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "message": str(e)}

logger.info("Routers included, application is ready.")
