import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings
from backend.database.models import Base

logger = logging.getLogger("research_platform.database")

# Translate MySQL or SQLite URL to async dialect
db_url = settings.DATABASE_URL
if db_url.startswith("mysql+pymysql://"):
    async_db_url = db_url.replace("mysql+pymysql://", "mysql+asyncmy://")
elif db_url.startswith("mysql://"):
    async_db_url = db_url.replace("mysql://", "mysql+asyncmy://")
elif db_url.startswith("sqlite://"):
    async_db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
else:
    async_db_url = db_url

engine_kwargs = {"echo": settings.DB_ECHO}
if not async_db_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    })

async_engine = create_async_engine(async_db_url, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize all schema tables."""
    async with async_engine.begin() as conn:
        logger.info("Initializing database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
