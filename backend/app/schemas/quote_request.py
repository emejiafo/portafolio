"""
Quote Request Schemas
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


class QuoteRequestBase(BaseModel):
    """Base quote request schema"""
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    project_type: Optional[str] = Field(None, max_length=100)
    budget_range: Optional[str] = Field(None, max_length=100)
    timeline: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=10, max_length=5000)

    @field_validator("name", "company", "project_type", "budget_range", "timeline", mode="before")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("description cannot be empty")
        return value


class QuoteRequestCreate(QuoteRequestBase):
    """Schema for creating a quote request (public submission)"""
    pass


class QuoteRequestUpdate(BaseModel):
    """Schema for updating a quote request (admin)"""
    status: Optional[str] = None
    notes: Optional[str] = None
    converted_project_id: Optional[UUID] = None


class QuoteRequestResponse(QuoteRequestBase):
    """Schema for quote request response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: str
    notes: Optional[str] = None
    converted_project_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class QuoteRequestListResponse(BaseModel):
    """Schema for paginated quote request list"""
    items: List[QuoteRequestResponse]
    total: int
    skip: int
    limit: int