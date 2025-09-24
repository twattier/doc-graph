"""
DocGraph API - Main FastAPI application module
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import health, documents, repositories
from .config import get_settings
from .database import init_postgres_connection, init_redis_connection, init_neo4j_connection, close_database_connections


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    print("🚀 DocGraph API starting up...")

    try:
        # Initialize database connections
        await init_postgres_connection()
        await init_redis_connection()
        await init_neo4j_connection()
        print("✅ Database connections initialized")
    except Exception as e:
        print(f"❌ Failed to initialize database connections: {e}")

    yield

    # Shutdown
    print("👋 DocGraph API shutting down...")

    try:
        # Close database connections
        await close_database_connections()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"❌ Error closing database connections: {e}")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title="DocGraph API",
        description="AI-powered document insight engine API",
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(repositories.router, tags=["repositories"])

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        # Log the actual error for debugging but don't expose it
        import logging
        logging.error(f"Unhandled exception: {exc}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "internal_error"
            }
        )

    return app


# Create the FastAPI app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )