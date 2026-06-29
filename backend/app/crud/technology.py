"""
Technology CRUD Operations
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.technology import Technology
from app.schemas.technology import TechnologyCreate, TechnologyUpdate


class CRUDTechnology(CRUDBase[Technology, TechnologyCreate, TechnologyUpdate]):
    """CRUD operations for Technology model"""

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Technology]:
        """Get a technology by name"""
        result = await db.execute(select(Technology).where(Technology.name == name))
        return result.scalar_one_or_none()

    async def get_by_category(
        self, db: AsyncSession, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[Technology]:
        """Get technologies by category"""
        result = await db.execute(
            select(Technology)
            .where(Technology.category == category)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


technology = CRUDTechnology(Technology)