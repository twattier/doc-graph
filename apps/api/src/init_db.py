"""
Database initialization script for creating tables.
"""
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from .models.base import Base
from .models.user import User, UserSession
from .models.repository import Repository, RepositoryVersion, ImportJob
from .config import get_settings


async def create_tables():
    """Create all database tables."""
    settings = get_settings()

    # Convert postgres URL to asyncpg URL for async operations
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=False,
    )

    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Successfully created database tables")

    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()


async def drop_tables():
    """Drop all database tables."""
    settings = get_settings()

    # Convert postgres URL to asyncpg URL for async operations
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=False,
    )

    try:
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("Successfully dropped database tables")

    except Exception as e:
        print(f"Error dropping tables: {e}")
        raise
    finally:
        await engine.dispose()


async def init_test_db():
    """Initialize database for testing."""
    await drop_tables()
    await create_tables()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(init_test_db())
    else:
        asyncio.run(create_tables())