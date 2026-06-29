"""
Technology Schemas
"""
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TechnologyBase(BaseModel):
    """Base technology schema"""
    name: str
    category: Optional[str] = None
    icon_url: Optional[str] = None
    color: Optional[str] = None


class TechnologyCreate(TechnologyBase):
    """Schema for creating a technology"""
    pass


class TechnologyUpdate(BaseModel):
    """Schema for updating a technology"""
    name: Optional[str] = None
    category: Optional[str] = None
    icon_url: Optional[str] = None
    color: Optional[str] = None


class TechnologyResponse(TechnologyBase):
    """Schema for technology response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID


class TechnologyListResponse(BaseModel):
    """Schema for paginated technology list"""
    items: List[TechnologyResponse]
    total: int
    skip: int
    limit: int