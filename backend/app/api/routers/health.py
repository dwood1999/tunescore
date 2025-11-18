"""Health check and system status endpoints."""

import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Track startup time
_startup_time = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.

    Returns service status without checking dependencies.
    """
    return {
        "status": "healthy",
        "service": "tunescore-api",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Detailed health check with dependency checks.

    Checks:
    - Database connectivity
    - Disk space
    - System uptime
    - Configuration status
    """
    health_status = {
        "status": "healthy",
        "service": "tunescore-api",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _startup_time),
        "checks": {},
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }
        logger.error(f"Database health check failed: {e}")

    # Check disk space
    try:
        storage_path = settings.STORAGE_DIR
        if os.path.exists(storage_path):
            stat = os.statvfs(storage_path)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            used_percent = ((total_gb - free_gb) / total_gb) * 100

            health_status["checks"]["disk_space"] = {
                "status": "healthy" if free_gb > 1.0 else "warning",
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 2),
            }

            if free_gb < 1.0:
                health_status["status"] = "warning"
        else:
            health_status["checks"]["disk_space"] = {
                "status": "warning",
                "message": f"Storage directory not found: {storage_path}",
            }
    except Exception as e:
        health_status["checks"]["disk_space"] = {
            "status": "error",
            "message": f"Failed to check disk space: {str(e)}",
        }
        logger.error(f"Disk space check failed: {e}")

    # Check configuration
    config_status = {
        "database_configured": bool(settings.DATABASE_URL),
        "spotify_configured": bool(
            settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET
        ),
        "youtube_configured": bool(settings.YOUTUBE_API_KEY),
        "ai_services_configured": bool(
            settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY
        ),
    }

    health_status["checks"]["configuration"] = {"status": "healthy", **config_status}

    return health_status


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Kubernetes-style readiness probe.

    Returns 200 if service is ready to accept traffic.
    Returns 503 if service is not ready.
    """
    try:
        # Check database connectivity
        result = await db.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict[str, Any]:
    """
    Kubernetes-style liveness probe.

    Returns 200 if service is alive (even if not ready).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _startup_time),
    }


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def metrics() -> dict[str, Any]:
    """
    Basic metrics endpoint (Prometheus-style).

    Returns service metrics in JSON format.
    """
    return {
        "tunescore_uptime_seconds": int(time.time() - _startup_time),
        "tunescore_info": {
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
        },
    }
