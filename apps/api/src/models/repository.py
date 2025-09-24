"""
Database models for repository management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

from .base import Base


class Repository(Base):
    """Database model for imported repositories."""

    __tablename__ = "repositories"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    branch = Column(String, nullable=False, default="main")
    commit_hash = Column(String, nullable=False)
    file_count = Column(Integer, default=0)
    total_size = Column(Integer, default=0)

    # Status tracking
    status = Column(String, nullable=False, default="active")  # active, syncing, error

    # Timestamps
    imported_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Future: User ownership (for basic user management)
    user_email = Column(String, nullable=True)


class RepositoryVersion(Base):
    """Database model for repository version history."""

    __tablename__ = "repository_versions"

    id = Column(String, primary_key=True)
    repository_id = Column(String, nullable=False)
    commit_hash = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    file_count = Column(Integer, default=0)
    total_size = Column(Integer, default=0)
    changes_summary = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class ImportJob(Base):
    """Database model for tracking import jobs."""

    __tablename__ = "import_jobs"

    id = Column(String, primary_key=True)
    repository_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, cloning, processing, completed, failed
    progress = Column(Integer, default=0)
    message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # User information
    user_email = Column(String, nullable=True)


# Pydantic models for API responses
class RepositoryResponse(BaseModel):
    """Response model for repository data."""
    id: str
    name: str
    owner: str
    url: str
    description: Optional[str] = None
    branch: str
    commit_hash: str
    file_count: int
    total_size: int
    status: str
    imported_at: datetime
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImportJobResponse(BaseModel):
    """Response model for import job status."""
    id: str
    repository_id: str
    url: str
    status: str
    progress: int
    message: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RepositoryImportRequest(BaseModel):
    """Request model for repository import."""
    url: str


class RepositoryImportResponse(BaseModel):
    """Response model for import initiation."""
    import_id: str
    message: str


class ImportStatusResponse(BaseModel):
    """Response model for import status check."""
    id: str
    status: str
    progress: int
    message: str
    repository: Optional[RepositoryResponse] = None