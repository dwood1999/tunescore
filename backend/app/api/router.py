"""Main API router."""

from fastapi import APIRouter

from ..industry_snapshot import routes as industry_pulse
from .routers import audio, auth, health, integrations, search, tracks, ai_tagging, monitoring, waitlist

api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tracks.router, prefix="/tracks", tags=["tracks"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(
    integrations.router, prefix="/integrations", tags=["integrations"]
)
api_router.include_router(
    industry_pulse.router, prefix="/industry-pulse", tags=["Industry Pulse"]
)
# AI Tagging (pitch generation, tags)
api_router.include_router(ai_tagging.router, tags=["AI Tagging"])

# AI Cost Monitoring
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])

# Waitlist
api_router.include_router(waitlist.router, tags=["Waitlist"])

# Additional routers can be added here as new features are developed
