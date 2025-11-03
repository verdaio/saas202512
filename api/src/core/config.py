"""
Core configuration settings for Pet Care API
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pet Care API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Multi-tenant scheduling platform for pet care professionals"

    # Server
    BACKEND_PORT: int = 8012
    HOST: str = "0.0.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5412/saas202512"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "saas202512"

    # Redis
    REDIS_URL: str = "redis://localhost:6412"

    # JWT Authentication
    JWT_SECRET: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Multi-Tenant
    TENANT_RESOLUTION: str = "subdomain"  # subdomain | header | path
    TENANT_HEADER_NAME: str = "X-Tenant-ID"
    TENANT_ISOLATION_LEVEL: str = "row"  # database | schema | row

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3012",
        "http://localhost:8012"
    ]

    # Stripe
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    ENABLE_PAYMENTS: bool = False

    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    ENABLE_SMS: bool = False

    # Feature Flags
    ENABLE_ANALYTICS: bool = False
    ENABLE_EMAIL: bool = False

    # Rate Limiting
    RATE_LIMIT_MAX: int = 100
    RATE_LIMIT_WINDOW: int = 15  # minutes

    class Config:
        env_file = ".env.local"
        case_sensitive = True


# Global settings instance
settings = Settings()
