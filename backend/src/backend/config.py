from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[BASE_DIR / ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_NAME: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    ASYNC_DATABASE_URL: str

    JWT_SECRET: str
    JWT_ACCESS_TOKEN_EXPIRES: int
    JWT_REFRESH_TOKEN_EXPIRES: int
    JWT_ALGORITHM: str

    MEDIA_DIR: str = str(BASE_DIR.parent / "media")
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "coremarket"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_WORKER_CONCURRENCY: int = 2
    CELERY_TASK_ALWAYS_EAGER: bool = False

    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "coremarket"
    SEARCH_ENABLED: bool = True

    # Observability — OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_ENDPOINT: str = "http://tempo:4317"
    OTEL_SERVICE_NAME: str = "coremarket-backend"

    # Observability — Prometheus
    PROMETHEUS_ENABLED: bool = True

    # Homepage precompute
    HOMEPAGE_SNAPSHOT_TTL: int = 600   # seconds; Redis TTL for computed payload
    HOMEPAGE_SNAPSHOT_KEY: str = "homepage:snapshot"

    # Telegram notifications
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_ALERTS_ENABLED: bool = False

@lru_cache
def get_settings() -> Settings:
    return Settings()