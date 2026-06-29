"""API v1 router (post-cleanup).

After Phase 4 cleanup, hour-tracker routes were removed from active
registration. Public portfolio features remain under /api/public.
"""
from fastapi import APIRouter

from app.api.v1.projects import router as projects_router

api_router = APIRouter()

# Keep minimal non-hour-tracker administrative routes.
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])