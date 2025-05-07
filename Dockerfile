# Build stage
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies (curl for healthchecks later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project definition files and source code for proper installation
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install dependencies and project in editable mode
RUN uv pip install --system -e .

# Runtime stage
FROM python:3.13-slim

# Install runtime dependencies for healthchecks and process management
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser && mkdir -p /app && chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy installed packages and project code
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/
# Copy pyproject.toml for metadata
COPY --chown=appuser:appuser pyproject.toml /app/

# Set default values for HOST and PORT environment variables.
# These will be used by the CMD if not overridden at runtime (e.g., via docker run -e).
ENV HOST "0.0.0.0"
ENV PORT "8000"
ENV LOG_LEVEL "INFO"
ENV RATE_LIMIT_PER_MINUTE "10" 

# Expose port (default, can be overridden at runtime)
EXPOSE ${PORT:-8000}

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV DEBUG=false
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Simple health check that will use configured values
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["sh", "-c", "exec uvicorn openai_api_blueprint.main:app --host \"${HOST}\" --port \"${PORT}\""]
