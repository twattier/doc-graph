"""
Database initialization script for creating tables.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

from .config import get_settings
from .models.base import Base
from .models.repository import Repository, ImportJob


async def create_tables():
    """Create all database tables."""
    settings = get_settings()

    # Create async engine for table creation
    engine = create_async_engine(
        settings.database_url,
        echo=True
    )

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("✅ Database tables created successfully")


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())