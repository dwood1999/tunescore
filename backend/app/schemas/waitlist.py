"""Waitlist schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class WaitlistCreate(BaseModel):
    """Schema for creating waitlist entry."""

    email: EmailStr
    name: str | None = None
    use_case: str | None = Field(
        None, description="creator, developer, or monetizer"
    )
    referral_source: str | None = Field(None, description="How did you hear about us?")


class WaitlistResponse(BaseModel):
    """Schema for waitlist response."""

    id: int
    email: str
    name: str | None
    use_case: str | None
    referral_source: str | None
    is_beta_tester: bool
    is_invited: bool
    created_at: datetime

    class Config:
        from_attributes = True

