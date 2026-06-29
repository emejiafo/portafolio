"""
Public Portfolio API Endpoints
"""
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.project import project as project_crud
from app.crud.technology import technology as tech_crud
from app.models.settings import ProfileInfo
from app.schemas.project import ProjectPublicResponse
from app.schemas.settings import PublicProfileResponse
from app.schemas.technology import TechnologyResponse

router = APIRouter()


def _parse_skills(raw_value: Optional[str]) -> List[str]:
    """Parse skills from either JSON array or comma-separated string."""
    if not raw_value:
        return []

    value = raw_value.strip()
    if not value:
        return []

    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass

    return [item.strip() for item in value.split(",") if item.strip()]


@router.get("/projects", response_model=List[ProjectPublicResponse])
async def list_public_projects(
    technology: Optional[str] = None,
    project_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List public portfolio projects"""
    projects = await project_crud.get_public(db, skip=0, limit=100)
    
    # Filter by technology if specified
    if technology:
        projects = [
            p for p in projects 
            if any(t.name.lower() == technology.lower() for t in p.technologies)
        ]
    
    # Filter by project type if specified
    if project_type:
        projects = [p for p in projects if p.project_type == project_type]

    for project in projects:
        project.assets = sorted(
            project.assets,
            key=lambda asset: (asset.sort_order, asset.created_at),
        )
    
    return projects


@router.get("/projects/{slug}", response_model=ProjectPublicResponse)
async def get_public_project(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a public project by slug"""
    project = await project_crud.get_by_slug(db, slug=slug)
    if not project or not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project.assets = sorted(
        project.assets,
        key=lambda asset: (asset.sort_order, asset.created_at),
    )

    return project


@router.get("/technologies", response_model=List[TechnologyResponse])
async def list_technologies(
    db: AsyncSession = Depends(get_db),
):
    """List all technologies for filtering"""
    technologies = await tech_crud.get_multi(db, skip=0, limit=1000)
    return technologies


@router.get("/profile", response_model=PublicProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
):
    """Get normalized public profile information."""
    result = await db.execute(
        select(ProfileInfo)
    )
    profile_items = result.scalars().all()

    profile_map = {item.key: item.value for item in profile_items}
    skills = _parse_skills(profile_map.get("skills"))

    return PublicProfileResponse(
        full_name=profile_map.get("full_name"),
        professional_title=profile_map.get("professional_title"),
        bio_short=profile_map.get("bio_short"),
        bio_full=profile_map.get("bio_full"),
        email=profile_map.get("email"),
        location=profile_map.get("location"),
        website_url=profile_map.get("website_url"),
        linkedin_url=profile_map.get("linkedin_url"),
        github_url=profile_map.get("github_url"),
        cv_url=profile_map.get("cv_url"),
        cv_label=profile_map.get("cv_label"),
        cv_updated_at=profile_map.get("cv_updated_at"),
        skills=skills,
    )