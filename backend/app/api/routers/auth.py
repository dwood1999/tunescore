"""Authentication endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_id,
    get_password_hash,
    verify_password,
)
from ...models.user import User
from ...schemas.auth import LoginRequest, RegisterRequest, Token, TokenRefresh, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate user and return JWT tokens.

    Returns:
        Token: Access and refresh tokens
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login attempt with non-existent email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        logger.warning(f"Login attempt with inactive account: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Invalid password attempt for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    logger.info(f"User logged in successfully: {user.email}")
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/register", response_model=Token, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Register a new user and return JWT tokens.

    Returns:
        Token: Access and refresh tokens
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
        tier="free",
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create tokens for automatic login after registration
    token_data = {"sub": str(new_user.id), "email": new_user.email}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    logger.info(f"New user registered: {new_user.email}")
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Refresh access token using refresh token.

    Returns:
        Token: New access and refresh tokens
    """
    # Decode refresh token
    decoded = decode_token(token_data.refresh_token)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Check token type
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Get user ID from token
    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Verify user exists and is active
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    new_token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(data=new_token_data)
    refresh_token = create_refresh_token(data=new_token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_endpoint(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get current authenticated user.

    This endpoint requires authentication.
    Returns user information for the authenticated user.
    """
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == current_user_id))
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

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=getattr(user, 'is_superuser', False),
        tier=getattr(user, 'tier', 'free'),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

