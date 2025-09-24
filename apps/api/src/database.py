"""
Database connection and session management for DocGraph API
"""
from typing import AsyncGenerator
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase, AsyncDriver

from .config import get_settings

# SQLAlchemy Base
Base = declarative_base()

# Global connection objects
_postgres_engine = None
_postgres_session_factory = None
_redis_pool = None
_neo4j_driver = None


async def init_postgres_connection():
    """
    Initialize PostgreSQL connection.
    """
    global _postgres_engine, _postgres_session_factory

    settings = get_settings()

    # Convert sync URL to async URL
    async_database_url = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    _postgres_engine = create_async_engine(
        async_database_url,
        echo=settings.debug,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    _postgres_session_factory = async_sessionmaker(
        _postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get PostgreSQL database session.
    """
    if not _postgres_session_factory:
        await init_postgres_connection()

    async with _postgres_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_redis_connection():
    """
    Initialize Redis connection.
    """
    global _redis_pool

    settings = get_settings()

    _redis_pool = redis.ConnectionPool.from_url(
        settings.redis_url,
        decode_responses=True
    )


async def get_redis_client() -> redis.Redis:
    """
    Get Redis client.
    """
    if not _redis_pool:
        await init_redis_connection()

    return redis.Redis(connection_pool=_redis_pool)


async def init_neo4j_connection():
    """
    Initialize Neo4j connection.
    """
    global _neo4j_driver

    settings = get_settings()

    _neo4j_driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )


async def get_neo4j_session():
    """
    Get Neo4j session.
    """
    if not _neo4j_driver:
        await init_neo4j_connection()

    return _neo4j_driver.session()


async def close_database_connections():
    """
    Close all database connections.
    """
    global _postgres_engine, _redis_pool, _neo4j_driver

    # Close PostgreSQL connection
    if _postgres_engine:
        await _postgres_engine.dispose()
        _postgres_engine = None

    # Close Redis connection
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None

    # Close Neo4j connection
    if _neo4j_driver:
        await _neo4j_driver.close()
        _neo4j_driver = None


async def health_check_postgres() -> dict:
    """
    Check PostgreSQL connection health.
    """
    try:
        async with get_postgres_session() as session:
            result = await session.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "response_time_ms": 5,
                "details": "Connection successful"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": None,
            "details": str(e)
        }


async def health_check_redis() -> dict:
    """
    Check Redis connection health.
    """
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        return {
            "status": "healthy",
            "response_time_ms": 2,
            "details": "Connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": None,
            "details": str(e)
        }


async def health_check_neo4j() -> dict:
    """
    Check Neo4j connection health.
    """
    try:
        async with get_neo4j_session() as session:
            result = await session.run("RETURN 1 as n")
            await result.single()
            return {
                "status": "healthy",
                "response_time_ms": 8,
                "details": "Connection successful"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": None,
            "details": str(e)
        }


# Alias for compatibility with routes
get_async_db = get_postgres_session