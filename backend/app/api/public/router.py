"""
Public API Router
"""
from fastapi import APIRouter

from app.api.public.contact import router as contact_router
from app.api.public.portfolio import router as portfolio_router

public_router = APIRouter()

public_router.include_router(portfolio_router, prefix="/portfolio", tags=["Public Portfolio"])
public_router.include_router(contact_router, prefix="/contact", tags=["Public Contact"])