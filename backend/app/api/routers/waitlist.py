"""Waitlist API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models.waitlist import WaitlistEntry
from ...schemas.waitlist import WaitlistCreate, WaitlistResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.post("", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
async def join_waitlist(
    entry: WaitlistCreate,
    db: AsyncSession = Depends(get_db),
) -> WaitlistEntry:
    """
    Add email to waitlist for beta access.

    Args:
        entry: Waitlist entry data
        db: Database session

    Returns:
        Created waitlist entry

    Raises:
        HTTPException: If email already exists
    """
    try:
        # Create waitlist entry
        db_entry = WaitlistEntry(
            email=entry.email,
            name=entry.name,
            use_case=entry.use_case,
            referral_source=entry.referral_source,
        )

        db.add(db_entry)
        await db.commit()
        await db.refresh(db_entry)

        logger.info(f"New waitlist signup: {entry.email} ({entry.use_case})")

        return db_entry

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered on waitlist",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding to waitlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join waitlist",
        )


@router.get("/count", response_model=dict[str, int])
async def get_waitlist_count(db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    """
    Get total waitlist count.

    Args:
        db: Database session

    Returns:
        Dictionary with total count
    """
    try:
        stmt = select(WaitlistEntry)
        result = await db.execute(stmt)
        entries = result.scalars().all()

        return {"total": len(entries)}

    except Exception as e:
        logger.error(f"Error getting waitlist count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get waitlist count",
        )

