# ==============================================================================
# TIER 3: AUDIO PROCESSING SERVICE (Final)
# Inherits from audio processing base image - minimal, cache-optimized
# ==============================================================================

FROM audio-processing-base:latest

# Copy application code (this layer changes most frequently)
# No heavy package installations here - all done in base image!
COPY ./shared /app/shared
COPY ./services/audioProcessingService /app/services/audioProcessingService

# Create data directories
RUN mkdir -p /app/data/audio /app/data/video

# Run the worker service as root
CMD ["python", "-m", "services.audioProcessingService.main"]