"""Project models."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.technology import Technology
    from app.models.project_asset import ProjectAsset


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(300),
        unique=True,
        nullable=False,
    )
    short_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    full_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        server_default="draft",
    )
    project_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    estimated_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    hourly_rate_mxn: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    fixed_budget_mxn: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    billing_type: Mapped[str | None] = mapped_column(
        String(50),
        default="fixed",
        server_default="fixed",
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )
    github_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    live_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    thumbnail_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    technologies: Mapped[List["Technology"]] = relationship(
        secondary="project_technologies",
        back_populates="projects",
    )
    assets: Mapped[List["ProjectAsset"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectTechnology(Base):
    """Many-to-many relationship between projects and technologies."""

    __tablename__ = "project_technologies"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    technology_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("technologies.id", ondelete="CASCADE"),
        primary_key=True,
    )
