"""
Core configuration for the application
"""
import secrets
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """

    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server
    SERVER_NAME: str = "Blui API"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    PHOTO_BASE_URL: str = "https://blui.elginbrian.com"
    DEBUG: bool = True

    # App Info
    APP_NAME: str = "Blui Expense Tracker API"
    APP_VERSION: str = "1.0.0"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React
        "http://localhost:8080",  # Vue
        "http://localhost:4200",  # Angular
        "http://localhost:5000",  # Android emulator
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite:///./blui.db"

    # JWT
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()