"""
Configuration module for DocGraph API
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application settings
    app_name: str = "DocGraph API"
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=True, validation_alias="DEBUG")

    # Database settings
    database_url: str = Field(
        default="postgresql://docgraph_user:secure_dev_password@localhost:5433/docgraph_dev",
        validation_alias="DATABASE_URL"
    )

    # Neo4j settings
    neo4j_uri: str = Field(
        default="bolt://localhost:7688",
        validation_alias="NEO4J_URI"
    )
    neo4j_user: str = Field(default="neo4j", validation_alias="NEO4J_USER")
    neo4j_password: str = Field(
        default="secure_dev_neo4j_password",
        validation_alias="NEO4J_PASSWORD"
    )

    # Redis settings
    redis_url: str = Field(
        default="redis://:secure_dev_redis_password@localhost:6380",
        validation_alias="REDIS_URL"
    )

    # Security settings
    jwt_secret: str = Field(
        default="generate-secure-random-key-for-development",
        validation_alias="JWT_SECRET"
    )
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    """
    return Settings()