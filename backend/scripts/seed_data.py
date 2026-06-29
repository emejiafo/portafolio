"""Seed development data for the public portfolio experience."""

import asyncio
import os
import sys
from uuid import uuid4

from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import async_session_maker
from app.models.project import Project
from app.models.project_asset import ProjectAsset
from app.models.settings import ProfileInfo
from app.models.technology import Technology


TECHNOLOGIES = [
    {"name": "Python", "category": "language", "color": "#3776AB"},
    {"name": "FastAPI", "category": "framework", "color": "#009688"},
    {"name": "PostgreSQL", "category": "database", "color": "#336791"},
    {"name": "Docker", "category": "tool", "color": "#2496ED"},
    {"name": "Scikit-learn", "category": "framework", "color": "#F7931E"},
    {"name": "Pandas", "category": "library", "color": "#150458"},
    {"name": "NumPy", "category": "library", "color": "#013243"},
    {"name": "Plotly", "category": "library", "color": "#3F4F75"},
]

PROFILE_ENTRIES = [
    {"key": "full_name", "value": "Your Name", "category": "personal", "value_type": "text"},
    {
        "key": "professional_title",
        "value": "Machine Learning Engineer",
        "category": "professional",
        "value_type": "text",
    },
    {
        "key": "bio_short",
        "value": "I design and ship practical ML systems that improve business decisions.",
        "category": "professional",
        "value_type": "text",
    },
    {
        "key": "bio_full",
        "value": "I build data products from experimentation to production deployment.",
        "category": "professional",
        "value_type": "text",
    },
    {"key": "email", "value": "contact@example.com", "category": "contact", "value_type": "text"},
    {
        "key": "location",
        "value": "Mexico City, Mexico",
        "category": "personal",
        "value_type": "text",
    },
    {
        "key": "website_url",
        "value": "https://example.com",
        "category": "social",
        "value_type": "url",
    },
    {
        "key": "linkedin_url",
        "value": "https://linkedin.com/in/yourprofile",
        "category": "social",
        "value_type": "url",
    },
    {
        "key": "github_url",
        "value": "https://github.com/yourprofile",
        "category": "social",
        "value_type": "url",
    },
    {
        "key": "skills",
        "value": "Python, Machine Learning, FastAPI, MLOps, Data Visualization",
        "category": "professional",
        "value_type": "text",
    },
    {
        "key": "cv_url",
        "value": "/uploads/assets/cv/cv.pdf",
        "category": "professional",
        "value_type": "url",
    },
    {"key": "cv_label", "value": "View CV", "category": "professional", "value_type": "text"},
    {
        "key": "cv_updated_at",
        "value": "2026-06-26",
        "category": "professional",
        "value_type": "text",
    },
]

PROJECTS = [
    {
        "title": "Customer Churn Prediction Platform",
        "slug": "customer-churn-prediction-platform",
        "short_description": "Predicted subscriber churn with explainable risk segments and weekly alerts.",
        "full_description": "Built an end-to-end churn workflow from feature engineering to API serving and dashboard monitoring.",
        "project_type": "ml",
        "github_url": "https://github.com/example/churn-prediction",
        "live_url": "https://demo.example.com/churn",
        "display_order": 1,
        "technologies": ["Python", "Scikit-learn", "FastAPI", "PostgreSQL", "Docker"],
        "assets": [
            {
                "asset_type": "image",
                "file_path": "/uploads/assets/projects/churn-dashboard.png",
                "original_filename": "churn-dashboard.png",
                "mime_type": "image/png",
                "sort_order": 0,
            }
        ],
    },
    {
        "title": "Retail Demand Forecasting Pipeline",
        "slug": "retail-demand-forecasting-pipeline",
        "short_description": "Forecasted multi-store demand to improve replenishment and reduce stockouts.",
        "full_description": "Implemented a production-ready forecasting pipeline with seasonal baselines and automated reporting.",
        "project_type": "data_science",
        "github_url": "https://github.com/example/demand-forecasting",
        "live_url": "https://demo.example.com/forecasting",
        "display_order": 2,
        "technologies": ["Python", "Pandas", "NumPy", "Plotly", "Docker"],
        "assets": [
            {
                "asset_type": "image",
                "file_path": "/uploads/assets/projects/forecast-overview.png",
                "original_filename": "forecast-overview.png",
                "mime_type": "image/png",
                "sort_order": 0,
            }
        ],
    },
]


async def seed_technologies(db):
    """Create missing technologies and return lookup by name."""
    result = await db.execute(select(Technology))
    existing = {tech.name: tech for tech in result.scalars().all()}

    created = 0
    for tech_data in TECHNOLOGIES:
        name = tech_data["name"]
        if name in existing:
            continue
        tech = Technology(id=uuid4(), **tech_data)
        db.add(tech)
        existing[name] = tech
        created += 1

    await db.commit()
    print(f"Technologies: {created} created, {len(existing)} total")
    return existing


async def seed_profile_info(db):
    """Create missing profile keys required by the public profile endpoint."""
    keys = [entry["key"] for entry in PROFILE_ENTRIES]
    result = await db.execute(select(ProfileInfo).where(ProfileInfo.key.in_(keys)))
    existing = {row.key: row for row in result.scalars().all()}

    created = 0
    updated = 0
    for entry_data in PROFILE_ENTRIES:
        row = existing.get(entry_data["key"])
        if row is None:
            db.add(ProfileInfo(id=uuid4(), **entry_data))
            created += 1
            continue

        # Only patch incomplete values to avoid overwriting user-customized profile data.
        if not row.value:
            row.value = entry_data["value"]
            row.value_type = entry_data["value_type"]
            row.category = entry_data["category"]
            updated += 1

    await db.commit()
    print(f"Profile info: {created} created, {updated} updated")


async def seed_public_projects(db, tech_by_name):
    """Seed at least two public portfolio projects with technologies and assets."""
    created = 0
    for project_data in PROJECTS:
        existing_result = await db.execute(
            select(Project).where(Project.slug == project_data["slug"])
        )
        existing_project = existing_result.scalar_one_or_none()
        if existing_project:
            continue

        project = Project(
            id=uuid4(),
            title=project_data["title"],
            slug=project_data["slug"],
            short_description=project_data["short_description"],
            full_description=project_data["full_description"],
            status="completed",
            project_type=project_data["project_type"],
            is_public=True,
            github_url=project_data["github_url"],
            live_url=project_data["live_url"],
            display_order=project_data["display_order"],
        )

        project.technologies = [
            tech_by_name[name] for name in project_data["technologies"] if name in tech_by_name
        ]

        db.add(project)
        await db.flush()

        for asset in project_data["assets"]:
            db.add(
                ProjectAsset(
                    id=uuid4(),
                    project_id=project.id,
                    asset_type=asset["asset_type"],
                    file_path=asset["file_path"],
                    original_filename=asset["original_filename"],
                    mime_type=asset["mime_type"],
                    sort_order=asset["sort_order"],
                )
            )

        created += 1

    await db.commit()
    print(f"Public projects: {created} created")


async def main():
    print("Seeding portfolio development data...")
    async with async_session_maker() as db:
        tech_by_name = await seed_technologies(db)
        await seed_profile_info(db)
        await seed_public_projects(db, tech_by_name)
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
