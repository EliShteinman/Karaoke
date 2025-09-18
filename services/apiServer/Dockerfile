# ==============================================================================
# TIER 3: API SERVER SERVICE (Final)
# Inherits from root base image - minimal, cache-optimized
# ==============================================================================

FROM my-project-root-base:latest

# Switch to root for installation and file operations
USER root

# Install service-specific lightweight dependencies only
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    httpx \
    aiohttp

# Copy application code (this layer changes most frequently)
COPY ./shared /app/shared
COPY ./services/apiServer /app/services/apiServer

# Set proper ownership
RUN chown -R app:app /app

# Switch back to app user
USER app

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Expose the port
EXPOSE ${PORT}

# Run the FastAPI application
CMD ["sh", "-c", "uvicorn services.apiServer.app.main:app --host ${HOST} --port ${PORT}"]