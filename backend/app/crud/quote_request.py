"""
Quote Request CRUD Operations
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.quote_request import QuoteRequest
from app.schemas.quote_request import QuoteRequestCreate, QuoteRequestUpdate


class CRUDQuoteRequest(CRUDBase[QuoteRequest, QuoteRequestCreate, QuoteRequestUpdate]):
    """CRUD operations for QuoteRequest model"""

    async def get_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[QuoteRequest]:
        """Get quote requests by status"""
        result = await db.execute(
            select(QuoteRequest)
            .where(QuoteRequest.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_email(
        self, db: AsyncSession, *, email: str, skip: int = 0, limit: int = 100
    ) -> List[QuoteRequest]:
        """Get quote requests by email"""
        result = await db.execute(
            select(QuoteRequest)
            .where(QuoteRequest.email == email)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_pending(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[QuoteRequest]:
        """Get new/pending quote requests"""
        return await self.get_by_status(db, status="pending", skip=skip, limit=limit)

    async def convert_to_project(
        self, db: AsyncSession, *, db_obj: QuoteRequest, project_id: UUID
    ) -> QuoteRequest:
        """Mark quote as converted to project"""
        db_obj.status = "converted"
        db_obj.converted_project_id = project_id
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


quote_request = CRUDQuoteRequest(QuoteRequest)