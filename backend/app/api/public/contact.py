"""
Public Contact/Quote API Endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.quote_request import quote_request as quote_crud
from app.schemas.quote_request import QuoteRequestCreate, QuoteRequestResponse

router = APIRouter()


@router.post("/quote", response_model=QuoteRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_quote_request(
    quote_in: QuoteRequestCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit a quote request from the public contact form"""
    quote = await quote_crud.create(db, obj_in=quote_in)
    return quote