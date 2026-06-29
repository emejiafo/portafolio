"""Import all models here for Alembic to detect them."""

from app.db.base_class import Base
from app.models.project import Project, ProjectTechnology
from app.models.project_asset import ProjectAsset
from app.models.technology import Technology
from app.models.quote_request import QuoteRequest
from app.models.settings import AppSettings, ProfileInfo