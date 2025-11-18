"""Security utilities for authentication and authorization."""

from collections.abc import AsyncGenerator
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode, settings.get_jwt_secret(), algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in token

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode, settings.get_jwt_secret(), algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Optional[dict]: Decoded token data or None if invalid
    """
    try:
        return jwt.decode(
            token, settings.get_jwt_secret(), algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None


# HTTP Bearer for JWT tokens
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int:
    """
    Extract and validate user ID from JWT token.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        int: User ID from token

    Raises:
        HTTPException: If token is invalid
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not credentials:
        logger.warning("No credentials provided in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    logger.debug(f"Attempting to decode token: {token[:20]}...")
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from token
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user_id_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int | None:
    """
    Extract and validate user ID from JWT token (optional).
    
    Returns None if no credentials provided, otherwise validates and returns user ID.

    Args:
        credentials: HTTP Authorization credentials (optional)

    Returns:
        int | None: User ID from token, or None if not authenticated

    Raises:
        HTTPException: If token is provided but invalid
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from token
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        return int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _get_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """Import get_db here to avoid circular imports."""
    from .database import get_db

    async for db in get_db():
        yield db


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(_get_db_dependency),
) -> Any:
    """
    Get current authenticated user from database.

    This dependency validates the JWT token and fetches the user from the database.
    Use it in protected route dependencies.

    Args:
        user_id: User ID from JWT token (injected via dependency)
        db: Database session (injected via dependency)

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If user not found or inactive
    """
    # Import here to avoid circular imports
    from ..models.user import User

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user
