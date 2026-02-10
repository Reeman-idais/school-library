# Multi-stage Dockerfile for school-library application

# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files (required so Poetry can install the local package)
COPY pyproject.toml poetry.lock* ./
# Copy the rest of the project so the package is available for installation
COPY . .

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies (Poetry will install the package as well)
RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create logs directory
RUN mkdir -p logs && chown -R appuser:appuser logs

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8000); conn.request('GET', '/health'); conn.getresponse()"

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Default command: run the application web UI (recommended)
CMD ["python", "run_app.py"]
