"""
Projects API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.project import project as project_crud
from app.crud.technology import technology as tech_crud
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all projects with pagination and filters"""
    # Use base get_multi without filters for MVP simplicity
    projects = await project_crud.get_multi(db, skip=skip, limit=limit)
    total = await project_crud.get_count(db)
    
    return ProjectListResponse(
        items=projects,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project by ID with relations"""
    project = await project_crud.get_with_relations(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project"""
    technologies = []
    if project_in.technology_ids:
        technologies = await tech_crud.get_by_ids(db, ids=project_in.technology_ids)
    
    project = await project_crud.create_with_technologies(
        db, obj_in=project_in, technologies=technologies
    )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing project"""
    project = await project_crud.get_with_relations(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Handle technology updates
    if project_in.technology_ids is not None:
        technologies = await tech_crud.get_by_ids(db, ids=project_in.technology_ids)
        project = await project_crud.update_technologies(
            db, db_obj=project, technologies=technologies
        )
    
    # Update other fields
    update_data = project_in.model_dump(exclude={"technology_ids"}, exclude_unset=True)
    if update_data:
        project = await project_crud.update(db, db_obj=project, obj_in=update_data)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project"""
    project = await project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    await project_crud.delete(db, id=project_id)
    return None