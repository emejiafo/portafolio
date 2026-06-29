"""
Seed sample data for development
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.technology import Technology
from app.models.settings import ProfileInfo, AppSettings
from app.models.project import Project
from uuid import uuid4


async def seed_technologies(db: AsyncSession):
    """Seed common technologies"""
    technologies = [
        {"name": "Python", "category": "language", "color": "#3776AB"},
        {"name": "TensorFlow", "category": "framework", "color": "#FF6F00"},
        {"name": "PyTorch", "category": "framework", "color": "#EE4C2C"},
        {"name": "Scikit-learn", "category": "framework", "color": "#F7931E"},
        {"name": "Pandas", "category": "library", "color": "#150458"},
        {"name": "NumPy", "category": "library", "color": "#013243"},
        {"name": "FastAPI", "category": "framework", "color": "#009688"},
        {"name": "PostgreSQL", "category": "database", "color": "#336791"},
        {"name": "Docker", "category": "tool", "color": "#2496ED"},
        {"name": "GCP", "category": "cloud", "color": "#4285F4"},
        {"name": "AWS", "category": "cloud", "color": "#FF9900"},
        {"name": "Gradio", "category": "framework", "color": "#F97316"},
        {"name": "Streamlit", "category": "framework", "color": "#FF4B4B"},
        {"name": "Plotly", "category": "library", "color": "#3F4F75"},
        {"name": "SQL", "category": "language", "color": "#CC2927"},
    ]
    
    for tech_data in technologies:
        tech = Technology(id=uuid4(), **tech_data)
        db.add(tech)
    
    await db.commit()
    print(f"✅ Seeded {len(technologies)} technologies")


async def seed_profile_info(db: AsyncSession):
    """Seed profile information"""
    profile_entries = [
        {"key": "full_name", "value": "Your Name", "category": "personal"},
        {"key": "professional_title", "value": "Data Scientist & ML Engineer", "category": "professional"},
        {"key": "bio_short", "value": "Passionate data scientist specializing in machine learning and AI solutions.", "category": "professional"},
        {"key": "bio_full", "value": "# About Me\n\nI'm a data scientist based in Mexico City with expertise in machine learning, deep learning, and data analysis.", "category": "professional", "value_type": "markdown"},
        {"key": "email", "value": "contact@example.com", "category": "contact"},
        {"key": "linkedin_url", "value": "https://linkedin.com/in/yourprofile", "category": "social"},
        {"key": "github_url", "value": "https://github.com/yourprofile", "category": "social"},
        {"key": "location", "value": "Mexico City, Mexico", "category": "personal"},
    ]
    
    for entry_data in profile_entries:
        entry = ProfileInfo(id=uuid4(), **entry_data)
        db.add(entry)
    
    await db.commit()
    print(f"✅ Seeded {len(profile_entries)} profile entries")


async def seed_app_settings(db: AsyncSession):
    """Seed application settings"""
    settings_data = [
        {"key": "invoice_prefix", "value": "INV", "description": "Prefix for invoice numbers"},
        {"key": "default_iva_rate", "value": "16", "description": "Default IVA rate (%)"},
        {"key": "default_payment_terms", "value": "15", "description": "Default payment terms (days)"},
        {"key": "business_name", "value": "Your Business Name", "description": "Business name for invoices"},
        {"key": "business_rfc", "value": "XXXX000000XXX", "description": "Business RFC"},
        {"key": "currency", "value": "MXN", "description": "Default currency"},
    ]
    
    for setting_data in settings_data:
        setting = AppSettings(id=uuid4(), **setting_data)
        db.add(setting)
    
    await db.commit()
    print(f"✅ Seeded {len(settings_data)} app settings")


async def seed_sample_project(db: AsyncSession):
    """Seed a sample project"""
    project = Project(
        id=uuid4(),
        title="Sample ML Project",
        slug="sample-ml-project",
        short_description="A sample machine learning project for portfolio demonstration.",
        full_description="# Sample ML Project\n\nThis is a detailed description of the project...",
        status="completed",
        project_type="ml_model",
        billing_type="fixed",
        is_public=True,
        display_order=1,
    )
    db.add(project)
    await db.commit()
    print("✅ Seeded sample project")


async def main():
    """Run all seed functions"""
    print("🌱 Starting database seeding...")
    
    async with async_session() as db:
        await seed_technologies(db)
        await seed_profile_info(db)
        await seed_app_settings(db)
        await seed_sample_project(db)
    
    print("✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())