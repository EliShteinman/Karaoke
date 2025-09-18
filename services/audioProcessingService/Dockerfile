# ==============================================================================
# TIER 3: AUDIO PROCESSING SERVICE (Final)
# Inherits from audio processing base image - minimal, cache-optimized
# ==============================================================================

FROM audio-processing-base:latest

# Switch to root for file operations only
USER root

# Copy application code (this layer changes most frequently)
# No heavy package installations here - all done in base image!
COPY ./shared /app/shared
COPY ./services/audioProcessingService /app/services/audioProcessingService

# Set proper ownership
RUN chown -R app:app /app

# Switch back to app user
USER app

# Run the worker service
CMD ["python", "-m", "services.audioProcessingService.main"]