"""
DocGraph API - Main FastAPI application module
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import health, documents, repositories, users
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
        description="""
        ## DocGraph API - AI-Powered Document Insight Engine

        The DocGraph API provides comprehensive Git repository import and analysis capabilities,
        enabling users to import public repositories, analyze their structure, and extract
        meaningful insights from project documentation.

        ### Features

        - **Git Repository Import**: Import public repositories from GitHub, GitLab, and other Git services
        - **Repository Management**: Full CRUD operations for managing imported repositories
        - **Document Analysis**: AI-powered analysis of project documentation and code structure
        - **User Management**: Email-based authentication and user session management
        - **Health Monitoring**: Real-time health checks for all system components

        ### Authentication

        Most endpoints require authentication via JWT tokens. Include the token in the
        `Authorization` header as: `Bearer <token>`

        ### Rate Limiting

        Repository import endpoints are rate limited to 10 imports per minute per user
        to ensure system stability.

        ### API Status

        - **Environment**: {environment}
        - **Version**: 0.1.0
        - **Health Check**: GET /health
        """.format(environment=settings.environment.title()),
        version="0.1.0",
        contact={
            "name": "DocGraph Development Team",
            "url": "https://github.com/your-org/doc-graph",
        },
        license_info={
            "name": "MIT",
        },
        tags_metadata=[
            {
                "name": "health",
                "description": "System health and monitoring endpoints",
            },
            {
                "name": "repositories",
                "description": "Git repository import, management, and analysis operations",
            },
            {
                "name": "users",
                "description": "User authentication, registration, and session management",
            },
            {
                "name": "documents",
                "description": "Document management and analysis operations",
            },
        ],
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
    app.include_router(repositories.router)  # Already has prefix and tags
    app.include_router(users.router)  # Already has prefix and tags

    # Root endpoint
    @app.get("/", tags=["root"], summary="API Root", description="Get API information and available endpoints")
    async def root():
        """
        API root endpoint providing basic information and navigation links.
        """
        return {
            "message": "Welcome to DocGraph API",
            "version": "0.1.0",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_spec": "/openapi.json"
            },
            "health_check": "/health",
            "endpoints": {
                "repositories": "/api/repositories",
                "documents": "/api/documents",
                "users": "/api/users"
            },
            "features": [
                "Git repository import and management",
                "Document analysis and processing",
                "User authentication and sessions",
                "Rate limiting and security",
                "Real-time health monitoring"
            ]
        }

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