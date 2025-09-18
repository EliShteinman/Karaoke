# ==============================================================================
# TIER 3: STREAMLIT CLIENT SERVICE (Final)
# Inherits from root base image - minimal, cache-optimized
# ==============================================================================

FROM my-project-root-base:latest

# Install service-specific lightweight dependencies only
RUN pip install --no-cache-dir \
    streamlit \
    altair \
    pandas

# Copy application code
COPY ./shared /app/shared
COPY ./services/streamlitClient /app/services/streamlitClient

# Set working directory
WORKDIR /app

# Set environment variables
ENV PORT=8501

# Expose the port
EXPOSE ${PORT}

# Run the Streamlit application as root
CMD exec streamlit run services/streamlitClient/app.py --server.port ${PORT} --server.address 0.0.0.0