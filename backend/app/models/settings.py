"""Settings and profile info models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppSettings(Base):
    """Application settings key-value store."""

    __tablename__ = "app_settings"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ProfileInfo(Base):
    """Profile information key-value store."""

    __tablename__ = "profile_info"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    value_type: Mapped[str] = mapped_column(
        String(50),
        default="text",
        server_default="text",
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# Backwards compatibility alias for existing imports.
Settings = AppSettings