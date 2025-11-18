"""FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from .env file in project root
# This ensures API keys are available regardless of how the app is started
env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
    logging.info(f"Loaded environment from {env_file}")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .api.router import api_router
from .core.config import settings
from .core.database import close_database, init_database
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan manager"""
    # Startup
    logger.info("Starting TuneScore API...")
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down TuneScore API...")
    await close_database()
    logger.info("Database connections closed")


app = FastAPI(
    title="TuneScore",
    description="Bloomberg Terminal for the Music Industry - AI-powered intelligence platform",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Set up security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Extract hostnames from CORS origins
allowed_hosts = ["localhost", "127.0.0.1"]
for origin in settings.cors_origins:
    if origin.startswith(("http://", "https://")):
        host = (
            origin.replace("http://", "")
            .replace("https://", "")
            .split(":")[0]
            .split("/")[0]
        )
        if host and host not in allowed_hosts:
            allowed_hosts.append(host)

# Explicitly allow music.quilty.app (from Nginx proxy)
if "music.quilty.app" not in allowed_hosts:
    allowed_hosts.append("music.quilty.app")

# Allow requests from Nginx with any host when proxying
# TrustedHostMiddleware checks the Host header, but when behind a proxy,
# we need to trust the X-Forwarded-Host header as well
logger.info(f"Trusted hosts configured: {allowed_hosts}")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)

# Set up rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    calls=300,
    period=60,
    burst=50,
    auth_calls=50,
    auth_period=60,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TuneScore API - Bloomberg Terminal for the Music Industry",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "api_docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint."""
    from fastapi.responses import Response
    # Return a simple music note emoji as SVG
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🎵</text></svg>"""
    return Response(content=svg_content, media_type="image/svg+xml")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }
