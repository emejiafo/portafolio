"""
Application configuration using Pydantic Settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/freelance_db"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/freelance_db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    admin_password: str = "admin123"

    # Environment
    environment: str = "development"
    debug: bool = True
    allowed_hosts: List[str] = ["*"]

    # File Storage
    upload_dir: str = "/app/data/uploads"
    max_upload_size: int = 10485760  # 10MB

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Freelance Management API"

    # Email (optional)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None

    # Backwards/compat: allow legacy uppercase attribute access used by Alembic env.py
    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return self.database_url_sync


settings = Settings()