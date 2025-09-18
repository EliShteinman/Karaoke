# ==============================================================================
# TIER 1: ROOT BASE IMAGE (my-project-root-base)
# Contains shared system dependencies and common Python packages
# ==============================================================================

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install shared system dependencies
# ffmpeg: Required by youtubeService (yt-dlp), transcriptionService, audioProcessingService
# curl: Required for health checks and general utility
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install shared Python dependencies that are common across all services
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pydantic \
    kafka-python \
    elasticsearch \
    python-dotenv \
    requests

# Set Python path
ENV PYTHONPATH=/app

# This image serves as a base - no CMD needed