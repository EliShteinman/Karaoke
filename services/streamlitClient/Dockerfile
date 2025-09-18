# ==============================================================================
# TIER 3: STREAMLIT CLIENT SERVICE (Final)
# Inherits from root base image - minimal, cache-optimized
# ==============================================================================

FROM my-project-root-base:latest

# Switch to root for installation and file operations
USER root

# Install service-specific lightweight dependencies only
RUN pip install --no-cache-dir \
    streamlit \
    altair \
    pandas

# Copy application code (this layer changes most frequently)
COPY ./shared /app/shared
COPY ./services/streamlitClient /app/services/streamlitClient

# Set proper ownership
RUN chown -R app:app /app

# Switch back to app user
USER app

# Set environment variables
ENV PORT=8501

# Expose the port
EXPOSE ${PORT}

# Run the Streamlit application
CMD ["sh", "-c", "streamlit run services/streamlitClient/app.py --server.port ${PORT} --server.address 0.0.0.0"]