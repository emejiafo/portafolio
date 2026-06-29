"""Technology model."""

from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Technology(Base):
    """Technology model for tagging projects."""

    __tablename__ = "technologies"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    icon_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        secondary="project_technologies",
        back_populates="technologies",
    )