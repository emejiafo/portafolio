"""
Settings and profile info schemas."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SettingsBase(BaseModel):
    """Base settings schema."""
    key: str
    value: Optional[str] = None


class SettingsCreate(SettingsBase):
    """Schema for creating a setting."""
    pass


class SettingsUpdate(BaseModel):
    """Schema for updating a setting."""
    value: Optional[str] = None


class SettingsResponse(SettingsBase):
    """Schema for settings response."""
    id: UUID
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileInfoBase(BaseModel):
    """Base profile info schema."""
    key: str
    value: Optional[str] = None
    value_type: Optional[str] = "text"
    category: Optional[str] = None


class ProfileInfoCreate(ProfileInfoBase):
    """Schema for creating profile info."""
    pass


class ProfileInfoUpdate(BaseModel):
    """Schema for updating profile info."""
    value: Optional[str] = None
    value_type: Optional[str] = None
    category: Optional[str] = None


class ProfileInfoResponse(ProfileInfoBase):
    """Schema for profile info response."""
    id: UUID
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppSettingsBase(BaseModel):
    """Base app settings schema"""
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class AppSettingsCreate(AppSettingsBase):
    """Schema for creating app settings"""
    pass


class AppSettingsUpdate(BaseModel):
    """Schema for updating app settings"""
    value: Optional[str] = None
    description: Optional[str] = None


class AppSettingsResponse(AppSettingsBase):
    """Schema for app settings response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    updated_at: datetime


class PublicProfileResponse(BaseModel):
    """Public profile for portfolio display"""
    full_name: Optional[str] = None
    professional_title: Optional[str] = None
    bio_short: Optional[str] = None
    bio_full: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    cv_url: Optional[str] = None
    cv_label: Optional[str] = None
    cv_updated_at: Optional[str] = None
    skills: List[str] = Field(default_factory=list)