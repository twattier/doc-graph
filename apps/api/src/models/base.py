"""
Base models and schemas for DocGraph API
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field

# SQLAlchemy Base for database models
Base = declarative_base()


class BaseSchema(BaseModel):
    """
    Base schema with common fields and configuration.
    """

    class Config:
        from_attributes = True
        populate_by_name = True


class TimestampedSchema(BaseSchema):
    """
    Base schema with timestamp fields.
    """
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class HealthCheckResponse(BaseSchema):
    """
    Health check response schema.
    """
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    services: dict = Field(..., description="Service status details")


class ErrorResponse(BaseSchema):
    """
    Standard error response schema.
    """
    detail: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    code: Optional[str] = Field(None, description="Error code")