"""
User management API routes.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..models.user import (
    UserCreate,
    UserResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserSessionResponse
)
from ..services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])

# Initialize user service
user_service = UserService()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current authenticated user from Authorization header.

    Expected format: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization[7:]  # Remove "Bearer " prefix

    user = await user_service.validate_session(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Register a new user account.

    Creates a user with email-based authentication.
    """
    try:
        user = await user_service.create_user(db, user_data)
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")


@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Login user with email (simplified authentication).

    Returns user information and session token.
    """
    try:
        user, token, expires_at = await user_service.login_user(db, login_data.email)

        return UserLoginResponse(
            user=UserResponse.from_orm(user),
            token=token,
            expires_at=expires_at,
            message="Login successful"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Logout current user by invalidating session token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization[7:]  # Remove "Bearer " prefix

    success = await user_service.logout_user(db, token)

    if success:
        return {"message": "Logout successful"}
    else:
        return {"message": "Session not found or already expired"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return UserResponse.from_orm(current_user)


@router.get("/session/validate", response_model=UserSessionResponse)
async def validate_session(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Validate current session and return user info.

    Used by frontend to check if user is still logged in.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return UserSessionResponse(
            user=None,
            session_id="",
            expires_at=datetime.utcnow(),
            is_valid=False
        )

    token = authorization[7:]
    user = await user_service.validate_session(db, token)

    if user:
        # Get session info
        from sqlalchemy import select
        from ..models.user import UserSession

        result = await db.execute(
            select(UserSession).where(
                UserSession.token == token,
                UserSession.is_active == True
            )
        )
        session = result.scalar_one_or_none()

        return UserSessionResponse(
            user=UserResponse.from_orm(user),
            session_id=session.id if session else "",
            expires_at=session.expires_at if session else datetime.utcnow(),
            is_valid=True
        )
    else:
        return UserSessionResponse(
            user=None,
            session_id="",
            expires_at=datetime.utcnow(),
            is_valid=False
        )


@router.post("/sessions/cleanup")
async def cleanup_expired_sessions(
    db: AsyncSession = Depends(get_async_db),
):
    """Clean up expired sessions (admin endpoint)."""
    cleaned_count = await user_service.cleanup_expired_sessions(db)

    return {
        "message": f"Cleaned up {cleaned_count} expired sessions",
        "cleaned_count": cleaned_count
    }