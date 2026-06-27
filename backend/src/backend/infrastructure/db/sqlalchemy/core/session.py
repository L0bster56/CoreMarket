from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.backend.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
