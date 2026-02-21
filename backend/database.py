"""
Database connection and session management
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import pool
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/resume_verify'
)

# Convert to async URL if needed
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
elif DATABASE_URL.startswith('sqlite://'):
    DATABASE_URL = DATABASE_URL.replace('sqlite://', 'sqlite+aiosqlite:///', 1)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=pool.NullPool,
    future=True
)

# Create session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

# Base class for models
Base = declarative_base()

# Database dependency
async def get_db() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
