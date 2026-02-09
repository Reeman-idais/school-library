# Dockerfile لواجهة المستخدم الجديدة
# Dockerfile for new user interface
# يستخدم run_app.py بدلاً من web/server.py

FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --only main --no-interaction --no-ansi

FROM python:3.10-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser

COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser . .

RUN mkdir -p logs && chown -R appuser:appuser logs

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

USER appuser

EXPOSE 8000

# تشغيل واجهة المستخدم الجديدة
CMD ["python", "run_app.py", "8000"]
