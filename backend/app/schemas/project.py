"""Project schemas"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.technology import TechnologyResponse


# Base schema with common fields
class ProjectBase(BaseModel):
    title: str = Field(..., max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    full_description: Optional[str] = None
    status: Optional[str] = Field(default="lead", max_length=50)
    project_type: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    hourly_rate_mxn: Optional[Decimal] = None
    fixed_budget_mxn: Optional[Decimal] = None
    billing_type: Optional[str] = Field(default="fixed", max_length=20)
    is_public: Optional[bool] = False
    github_url: Optional[str] = Field(None, max_length=500)
    live_url: Optional[str] = Field(None, max_length=500)
    thumbnail_path: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = 0


class ProjectCreate(ProjectBase):
    technology_ids: Optional[List[UUID]] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    full_description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    project_type: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    hourly_rate_mxn: Optional[Decimal] = None
    fixed_budget_mxn: Optional[Decimal] = None
    billing_type: Optional[str] = Field(None, max_length=20)
    is_public: Optional[bool] = None
    github_url: Optional[str] = Field(None, max_length=500)
    live_url: Optional[str] = Field(None, max_length=500)
    thumbnail_path: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = None
    technology_ids: Optional[List[UUID]] = None


class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Public response - limited fields for portfolio
class ProjectPublicResponse(BaseModel):
    id: UUID
    title: str
    slug: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    project_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    display_order: Optional[int] = 0
    technologies: List[TechnologyResponse] = Field(default_factory=list)
    assets: List["ProjectAssetPublicResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    skip: int
    limit: int


class ProjectPublicListResponse(BaseModel):
    items: List[ProjectPublicResponse]
    total: int


class ProjectAssetPublicResponse(BaseModel):
    id: UUID
    asset_type: str
    file_path: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    sort_order: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# Project Asset schemas
class ProjectAssetBase(BaseModel):
    asset_type: str = Field(..., max_length=50)  # image, video, document, etc.
    file_path: str = Field(..., max_length=500)
    original_filename: Optional[str] = Field(None, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    file_size_bytes: Optional[int] = None
    display_order: Optional[int] = 0
    caption: Optional[str] = Field(None, max_length=500)
    is_primary: Optional[bool] = False


class ProjectAssetCreate(ProjectAssetBase):
    project_id: UUID


class ProjectAssetUpdate(BaseModel):
    asset_type: Optional[str] = Field(None, max_length=50)
    file_path: Optional[str] = Field(None, max_length=500)
    original_filename: Optional[str] = Field(None, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    file_size_bytes: Optional[int] = None
    display_order: Optional[int] = None
    caption: Optional[str] = Field(None, max_length=500)
    is_primary: Optional[bool] = None


class ProjectAssetResponse(ProjectAssetBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectAssetListResponse(BaseModel):
    items: List[ProjectAssetResponse]
    total: int