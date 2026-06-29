"""Phase 6 legacy table retirement.

Revision ID: 002_phase6
Revises: 001
Create Date: 2026-06-26 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "002_phase6"
down_revision = "001"
branch_labels = None
depends_on = None


LEGACY_TABLES = (
    "clients",
    "invoices",
    "invoice_items",
    "payments",
    "time_entries",
    "expenses",
)

LEGACY_DROP_ORDER = (
    "payments",
    "invoice_items",
    "time_entries",
    "expenses",
    "invoices",
    "clients",
)

ARCHIVE_PREFIX = "legacy_archive_"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _table_row_count(table_name: str) -> int:
    bind = op.get_bind()
    table_ident = _quote_identifier(table_name)
    return int(bind.execute(sa.text(f"SELECT COUNT(*) FROM {table_ident}")).scalar_one())


def _archive_table(table_name: str, existing_tables: set[str]) -> None:
    archive_name = f"{ARCHIVE_PREFIX}{table_name}"
    source_ident = _quote_identifier(table_name)
    archive_ident = _quote_identifier(archive_name)

    # Refresh archive data on re-run attempts so counts can be validated deterministically.
    if archive_name not in existing_tables:
        op.execute(
            sa.text(
                f"CREATE TABLE {archive_ident} AS TABLE {source_ident} WITH NO DATA"
            )
        )
        existing_tables.add(archive_name)
    else:
        op.execute(sa.text(f"TRUNCATE TABLE {archive_ident}"))

    op.execute(sa.text(f"INSERT INTO {archive_ident} SELECT * FROM {source_ident}"))

    source_count = _table_row_count(table_name)
    archive_count = _table_row_count(archive_name)
    if source_count != archive_count:
        raise RuntimeError(
            f"Archive validation failed for {table_name}: "
            f"source rows={source_count}, archive rows={archive_count}."
        )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    archived_tables: list[str] = []

    for table_name in LEGACY_TABLES:
        if table_name in existing_tables:
            _archive_table(table_name, existing_tables)
            archived_tables.append(table_name)

    if "projects" in existing_tables:
        project_columns = {col["name"] for col in inspector.get_columns("projects")}
        if "client_id" in project_columns:
            with op.batch_alter_table("projects") as batch_op:
                batch_op.drop_column("client_id")

    for table_name in LEGACY_DROP_ORDER:
        if table_name in archived_tables:
            op.drop_table(table_name)


def downgrade() -> None:
    raise RuntimeError(
        "Phase 6 retirement is intentionally irreversible via Alembic downgrade. "
        "Legacy data is archived in legacy_archive_* tables."
    )
