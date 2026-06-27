FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libc-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry>=2.0.0,<3.0.0" \
    && poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry lock && poetry install --no-root --no-interaction

COPY . .

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
