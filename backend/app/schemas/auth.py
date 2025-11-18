"""Authentication-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request schema."""

    refresh_token: str


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = Field(None, min_length=1, max_length=255)


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    tier: str

    class Config:
        from_attributes = True

