"""Database configuration"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://freelance:freelance_dev@db:5432/freelance_db"
)

DATABASE_URL_SYNC = os.getenv(
    "DATABASE_URL_SYNC", 
    "postgresql://freelance:freelance_dev@db:5432/freelance_db"
)

# Async engine for FastAPI
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Sync engine for Alembic migrations
engine = create_engine(DATABASE_URL_SYNC, echo=True)

# Async session factory
async_session_maker = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Alias for compatibility
AsyncSessionLocal = async_session_maker

Base = declarative_base()


async def get_db():
    """Dependency for getting async database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()