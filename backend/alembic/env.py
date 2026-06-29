"""
Alembic environment configuration
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, create_engine

from alembic import context

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.base import Base
from app.config import settings

# Import all models to ensure they're registered with Base.metadata
from app.models import (
    AppSettings,
    ProfileInfo,
    Project,
    ProjectAsset,
    ProjectTechnology,
    QuoteRequest,
    Technology,
)

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL - use sync version for Alembic
database_url = settings.DATABASE_URL_SYNC
if not database_url or '+asyncpg' in database_url:
    # Convert async URL to sync if needed
    database_url = settings.DATABASE_URL.replace('+asyncpg', '+psycopg2').replace('asyncpg', 'psycopg2')

config.set_main_option("sqlalchemy.url", database_url)

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()