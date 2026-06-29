"""
Project CRUD operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.project import Project
from app.models.project_asset import ProjectAsset
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """CRUD operations for projects."""

    async def get_with_relations(
        self, db: AsyncSession, *, id: UUID
    ) -> Optional[Project]:
        """Get project with all relations loaded."""
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.technologies),
                selectinload(self.model.assets),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(
        self, db: AsyncSession, *, slug: str
    ) -> Optional[Project]:
        """Get project by slug."""
        query = (
            select(self.model)
            .where(self.model.slug == slug)
            .options(
                selectinload(self.model.technologies),
                selectinload(self.model.assets),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_public(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Get public projects for portfolio."""
        query = (
            select(self.model)
            .where(self.model.is_public == True)
            .options(
                selectinload(self.model.technologies),
                selectinload(self.model.assets),
            )
            .order_by(self.model.display_order, self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_featured(
        self, db: AsyncSession, *, limit: int = 6
    ) -> List[Project]:
        """Get featured projects."""
        query = (
            select(self.model)
            .where(self.model.is_public == True, self.model.is_featured == True)
            .options(
                selectinload(self.model.technologies),
                selectinload(self.model.assets),
            )
            .order_by(self.model.display_order)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Project]:
        """Get multiple projects with optional filtering."""
        query = select(self.model).options(
            selectinload(self.model.technologies),
        )

        if status:
            query = query.where(self.model.status == status)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _generate_unique_slug(self, db: AsyncSession, title: str) -> str:
        """Generate a unique slug from title."""
        import re
        base_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        slug = base_slug
        counter = 1
        
        while True:
            # Check if slug exists
            existing = await self.get_by_slug(db, slug=slug)
            if not existing:
                return slug
            # Append counter and try again
            slug = f"{base_slug}-{counter}"
            counter += 1

    async def create_with_technologies(
        self,
        db: AsyncSession,
        *,
        obj_in: ProjectCreate,
        technologies: List = None,
    ) -> Project:
        """Create a project with optional technologies."""
        import uuid as uuid_module
        
        # Exclude technology_ids from the data since it's not a model field
        obj_data = obj_in.model_dump(exclude={"technology_ids"})
        
        # Generate UUID since DB default may not work
        obj_data["id"] = uuid_module.uuid4()
        
        # Generate unique slug if not provided
        if not obj_data.get("slug"):
            obj_data["slug"] = await self._generate_unique_slug(db, obj_data["title"])
        
        db_obj = self.model(**obj_data)
        
        if technologies:
            db_obj.technologies = technologies
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_technologies(
        self,
        db: AsyncSession,
        *,
        db_obj: Project,
        technologies: List,
    ) -> Project:
        """Update project technologies."""
        db_obj.technologies = technologies
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


project = CRUDProject(Project)