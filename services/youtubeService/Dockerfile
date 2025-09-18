# ==============================================================================
# TIER 3: YOUTUBE SERVICE (Final)
# Inherits from root base image - minimal, cache-optimized
# ==============================================================================

FROM my-project-root-base:latest

# Install service-specific lightweight dependencies only
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    yt-dlp \
    google-api-python-client

# Copy application code (this layer changes most frequently)
COPY ./shared /app/shared
COPY ./services/youtubeService /app/services/youtubeService

# Create data directories
RUN mkdir -p /app/data/audio /app/data/video

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8001

# Expose the port
EXPOSE ${PORT}

# Run the FastAPI application as root
CMD exec uvicorn services.youtubeService.app.main:app --host ${HOST} --port ${PORT}