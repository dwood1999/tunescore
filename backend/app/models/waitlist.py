"""Waitlist model for beta signups."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class WaitlistEntry(Base):
    """Waitlist entry for beta access."""

    __tablename__ = "waitlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    use_case: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # creator, developer, monetizer
    referral_source: Mapped[str | None] = mapped_column(String, nullable=True)
    is_beta_tester: Mapped[bool] = mapped_column(Boolean, default=False)
    is_invited: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    invited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<WaitlistEntry(email={self.email}, use_case={self.use_case})>"

