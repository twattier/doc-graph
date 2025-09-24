"""
User management models for authentication and project ownership.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean
from pydantic import BaseModel, EmailStr

from .base import Base


class User(Base):
    """Database model for users."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSession(Base):
    """Database model for user sessions."""

    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models for API
class UserCreate(BaseModel):
    """Request model for user creation."""
    email: EmailStr
    name: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr


class UserLoginResponse(BaseModel):
    """Response model for user login."""
    user: UserResponse
    token: str
    expires_at: datetime
    message: str


class UserSessionResponse(BaseModel):
    """Response model for session validation."""
    user: UserResponse
    session_id: str
    expires_at: datetime
    is_valid: bool