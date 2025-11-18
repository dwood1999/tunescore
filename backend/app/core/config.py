"""Application configuration settings."""

import logging
import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    JWT_SECRET: str  # Required from environment
    SECRET_KEY: str | None = None  # Legacy field - use JWT_SECRET

    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    def get_jwt_secret(self) -> str:
        """Canonical JWT secret accessor."""
        return self.JWT_SECRET

    # Database Configuration
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # Application URL Configuration
    APP_URL: str = Field(default="http://localhost:5128", env="FRONTEND_URL")

    # CORS Configuration
    BACKEND_CORS_ORIGINS_STR: str = Field(
        default="http://localhost:5128,http://127.0.0.1:5128",
        env="BACKEND_CORS_ORIGINS",
    )

    # Frontend port will be added dynamically
    FRONTEND_PORT: str = Field(default="5128", env="FRONTEND_PORT")
    DEV_FRONTEND_PORT: str = Field(default="5128", env="DEV_FRONTEND_PORT")

    @validator("BACKEND_CORS_ORIGINS_STR", pre=True)
    @classmethod
    def assemble_cors_origins(cls, v):
        """Assemble CORS origins from environment variable."""
        if v is None or v == "":
            return "http://localhost:5128,http://127.0.0.1:5128"
        if isinstance(v, str):
            return v
        return v

    @property
    def BACKEND_CORS_ORIGINS(self) -> str:
        """Backward compatibility property for BACKEND_CORS_ORIGINS."""
        return self.BACKEND_CORS_ORIGINS_STR

    def add_frontend_cors_origins(self) -> list[str]:
        """Add frontend port origins to CORS list."""
        frontend_port = getattr(self, "FRONTEND_PORT", "5128")
        dev_frontend_port = getattr(self, "DEV_FRONTEND_PORT", "5128")
        return [
            f"http://localhost:{frontend_port}",
            f"http://127.0.0.1:{frontend_port}",
            f"http://0.0.0.0:{frontend_port}",
            f"http://localhost:{dev_frontend_port}",
            f"http://127.0.0.1:{dev_frontend_port}",
            f"http://0.0.0.0:{dev_frontend_port}",
        ]

    # AI Services Configuration
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    # Music Industry Integrations
    SPOTIFY_CLIENT_ID: str | None = None
    SPOTIFY_CLIENT_SECRET: str | None = None
    SPOTIFY_REDIRECT_URI: str | None = None
    YOUTUBE_API_KEY: str | None = None

    # Application Configuration
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # File Storage Configuration
    STORAGE_DIR: str = "files"
    MAX_FILE_SIZE_MB: int = 500  # 500MB limit for audio files
    _allowed_file_types_str: str = ".mp3,.wav,.flac,.m4a,.ogg"

    @property
    def ALLOWED_FILE_TYPES(self) -> list[str]:
        """Parse allowed file types from string to list."""
        return [i.strip() for i in self._allowed_file_types_str.split(",")]

    # Analysis Configuration
    DEFAULT_AI_MODEL: str = "claude-3-5-sonnet-20241022"
    MAX_CONCURRENT_ANALYSES: int = 5
    ANALYSIS_TIMEOUT: int = 300  # 5 minutes

    # Safety Configuration
    VALIDATE_JSON: bool = True
    SCRUB_LOGS: bool = True
    LOG_MAX_LENGTH: int = 200

    # Cost Governor Configuration
    ANALYSIS_MAX_USD: float = 5.0
    USER_DAILY_MAX_USD: float = 50.0

    # Industry Pulse Configuration
    INDUSTRY_PULSE_ENABLED: bool = True
    INDUSTRY_PULSE_SCRAPER_INTERVAL_HOURS: int = 4
    INDUSTRY_PULSE_DIGEST_ENABLED: bool = True
    INDUSTRY_PULSE_MAX_COST_PER_DIGEST: float = 0.20
    SCRAPEOPS_API_KEY: str | None = None

    # Logging Configuration
    ENABLE_PROMPT_LOGGING: bool = True
    PROMPT_LOG_PATH: str = "logs/api_prompts.log"
    PROMPT_LOG_LEVEL: str = "INFO"
    PROMPT_LOG_MAX_SIZE_MB: int = 100
    PROMPT_LOG_RETENTION_DAYS: int = 30
    PROMPT_LOG_BACKUP_COUNT: int = 5

    # Environment detection
    ENV: str = Field(default_factory=lambda: os.getenv("ENV", "dev"))

    def get_analysis_max_usd(self) -> float:
        """Get maximum cost per analysis with safe fallback"""
        if self.ANALYSIS_MAX_USD is not None:
            return max(0.0, self.ANALYSIS_MAX_USD)
        return 5.0

    def get_user_daily_max_usd(self) -> float:
        """Get maximum cost per user per day with safe fallback"""
        if self.USER_DAILY_MAX_USD is not None:
            return max(0.0, self.USER_DAILY_MAX_USD)
        return 50.0

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() in ("production", "prod")

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "")

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins including APP_URL and development URLs."""
        origins = []

        if self.APP_URL and self.APP_URL not in origins:
            origins.append(self.APP_URL)

        if self.BACKEND_CORS_ORIGINS_STR:
            for origin in self.BACKEND_CORS_ORIGINS_STR.split(","):
                origin = origin.strip()
                if origin and origin not in origins:
                    origins.append(origin)

        origins.extend(self.add_frontend_cors_origins())

        return origins

    @validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v

    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
        env_file = ["../../.env", "../.env", ".env"]  # Prioritize tunescore .env


# Create settings instance
settings = Settings()

# Debug logging
logger = logging.getLogger(__name__)


def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings


if settings.LOG_LEVEL.upper() == "DEBUG":
    logger.debug("🔧 Environment variables loaded")
    logger.debug(
        f"   DATABASE_URL: {'✅ SET' if settings.DATABASE_URL else '❌ NOT SET'}"
    )
    logger.debug(
        f"   SPOTIFY_CLIENT_ID: {'✅ SET' if settings.SPOTIFY_CLIENT_ID else '❌ NOT SET'}"
    )
    logger.debug(
        f"   YOUTUBE_API_KEY: {'✅ SET' if settings.YOUTUBE_API_KEY else '❌ NOT SET'}"
    )
