"""
User management service for authentication and session handling.
"""

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from ..models.user import User, UserSession, UserCreate, UserLoginResponse, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management and authentication."""

    def __init__(self, session_duration_hours: int = 24):
        """Initialize user service.

        Args:
            session_duration_hours: Session duration in hours
        """
        self.session_duration = timedelta(hours=session_duration_hours)

    async def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Create a new user account.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            User: Created user object
        """
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Return existing user if already exists
            return existing_user

        # Create new user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            is_active=True,
            is_verified=True  # Auto-verify for now, can implement email verification later
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Created new user: {user.email}")
        return user

    async def login_user(self, db: Session, email: str) -> Tuple[User, str, datetime]:
        """
        Login user and create session (simplified email-based login).

        Args:
            db: Database session
            email: User email

        Returns:
            Tuple of (User, session_token, expires_at)
        """
        # Find or create user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Create user if doesn't exist
            user_create = UserCreate(email=email, name=email.split('@')[0])
            user = await self.create_user(db, user_create)

        if not user.is_active:
            raise ValueError("User account is deactivated")

        # Create new session
        session_token = secrets.token_urlsafe(32)
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + self.session_duration

        session = UserSession(
            id=session_id,
            user_id=user.id,
            token=session_token,
            expires_at=expires_at,
            is_active=True
        )

        db.add(session)

        # Update user last login
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(last_login_at=datetime.utcnow())
        )

        await db.commit()

        logger.info(f"User {user.email} logged in")
        return user, session_token, expires_at

    async def validate_session(self, db: Session, token: str) -> Optional[User]:
        """
        Validate a user session token.

        Args:
            db: Database session
            token: Session token

        Returns:
            User object if valid, None otherwise
        """
        # Find active session
        result = await db.execute(
            select(UserSession, User)
            .join(User, UserSession.user_id == User.id)
            .where(
                UserSession.token == token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        )

        session_data = result.first()
        if not session_data:
            return None

        session, user = session_data

        if not user.is_active:
            return None

        return user

    async def logout_user(self, db: Session, token: str) -> bool:
        """
        Logout user by invalidating session token.

        Args:
            db: Database session
            token: Session token to invalidate

        Returns:
            bool: True if logout successful
        """
        # Deactivate session
        result = await db.execute(
            update(UserSession)
            .where(UserSession.token == token)
            .values(is_active=False)
        )

        await db.commit()

        return result.rowcount > 0

    async def cleanup_expired_sessions(self, db: Session) -> int:
        """
        Clean up expired sessions from database.

        Args:
            db: Database session

        Returns:
            int: Number of sessions cleaned up
        """
        # Delete expired sessions
        result = await db.execute(
            UserSession.__table__.delete().where(
                UserSession.expires_at < datetime.utcnow()
            )
        )

        await db.commit()

        if result.rowcount > 0:
            logger.info(f"Cleaned up {result.rowcount} expired sessions")

        return result.rowcount

    async def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_user_sessions(self, db: Session, user_id: str) -> list[UserSession]:
        """List active sessions for a user."""
        result = await db.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
            .order_by(UserSession.created_at.desc())
        )

        return result.scalars().all()