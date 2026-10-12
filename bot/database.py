import logging
import asyncpg
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from bot import config

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

async def ensure_database_exists():
    """
    Verifies connection to the target database.
    Database 'expenses_bot' was created manually by the user in DBeaver.
    """
    try:
        conn = await asyncpg.connect(
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB
        )
        await conn.execute("SELECT 1")
        logger.info(f"Successfully connected to database '{config.POSTGRES_DB}'.")
        await conn.close()
    except Exception as e:
        logger.error(f"Could not connect to database '{config.POSTGRES_DB}': {e}")
        raise e

async_engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
