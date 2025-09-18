# ==============================================================================
# TIER 3: TRANSCRIPTION SERVICE (Final)
# Inherits from transcription base image - minimal, cache-optimized
# ==============================================================================

FROM transcription-base:latest

# Copy application code (this layer changes most frequently)
# No heavy package installations here - all done in base image!
COPY ./shared /app/shared
COPY ./services/transcriptionService /app/services/transcriptionService

# Create cache directories
RUN mkdir -p /app/cache/huggingface

# Set Hugging Face cache directory environment variables
ENV HF_HOME=/app/cache/huggingface
ENV TRANSFORMERS_CACHE=/app/cache/huggingface
ENV HF_HUB_CACHE=/app/cache/huggingface

# Run the worker service as root
CMD ["python", "-m", "services.transcriptionService.app.main"]
