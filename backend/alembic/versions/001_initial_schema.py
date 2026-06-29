"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('company', sa.String(200), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('rfc', sa.String(13), nullable=True),
        sa.Column('fiscal_regime', sa.String(10), nullable=True),
        sa.Column('cfdi_use', sa.String(10), nullable=True),
        sa.Column('address_street', sa.String(300), nullable=True),
        sa.Column('address_colony', sa.String(200), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(100), nullable=True),
        sa.Column('address_zip', sa.String(10), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clients_email', 'clients', ['email'])
    op.create_index('ix_clients_rfc', 'clients', ['rfc'])

    # Create technologies table
    op.create_table(
        'technologies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('slug', sa.String(300), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('full_description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='draft', nullable=False),
        sa.Column('project_type', sa.String(100), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('estimated_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('hourly_rate_mxn', sa.Numeric(12, 2), nullable=True),
        sa.Column('fixed_budget_mxn', sa.Numeric(12, 2), nullable=True),
        sa.Column('billing_type', sa.String(50), server_default='fixed', nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('github_url', sa.String(500), nullable=True),
        sa.Column('live_url', sa.String(500), nullable=True),
        sa.Column('thumbnail_path', sa.String(500), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_projects_status', 'projects', ['status'])
    op.create_index('ix_projects_is_public', 'projects', ['is_public'])

    # Create project_technologies junction table
    op.create_table(
        'project_technologies',
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('technology_id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('project_id', 'technology_id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['technology_id'], ['technologies.id'], ondelete='CASCADE')
    )

    # Create project_assets table
    op.create_table(
        'project_assets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('original_filename', sa.String(300), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE')
    )

    # Create quote_requests table
    op.create_table(
        'quote_requests',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('company', sa.String(200), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('project_type', sa.String(100), nullable=True),
        sa.Column('budget_range', sa.String(100), nullable=True),
        sa.Column('timeline', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(50), server_default='new', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('converted_project_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['converted_project_id'], ['projects.id'], ondelete='SET NULL')
    )
    op.create_index('ix_quote_requests_status', 'quote_requests', ['status'])

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('client_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('subtotal_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('iva_rate', sa.Numeric(5, 2), server_default='16.00'),
        sa.Column('iva_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('retention_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('retention_mxn', sa.Numeric(12, 2), server_default='0.00'),
        sa.Column('total_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', sa.String(50), server_default='draft', nullable=False),
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('sat_uuid', sa.String(36), nullable=True),
        sa.Column('pdf_path', sa.String(500), nullable=True),
        sa.Column('xml_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('invoice_number')
    )
    op.create_index('ix_invoices_status', 'invoices', ['status'])
    op.create_index('ix_invoices_issue_date', 'invoices', ['issue_date'])

    # Create invoice_items table
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit_price_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('amount_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('sat_product_code', sa.String(20), nullable=True),
        sa.Column('sat_unit_code', sa.String(10), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE')
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=False),
        sa.Column('amount_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('reference', sa.String(200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE')
    )

    # Create time_entries table
    op.create_table(
        'time_entries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('hours', sa.Numeric(5, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('billable', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('invoiced', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='SET NULL')
    )
    op.create_index('ix_time_entries_date', 'time_entries', ['date'])

    # Create expenses table
    op.create_table(
        'expenses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('amount_mxn', sa.Numeric(12, 2), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('receipt_path', sa.String(500), nullable=True),
        sa.Column('is_deductible', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL')
    )
    op.create_index('ix_expenses_date', 'expenses', ['date'])
    op.create_index('ix_expenses_category', 'expenses', ['category'])

    # Create profile_info table
    op.create_table(
        'profile_info',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(50), server_default='text'),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Create app_settings table
    op.create_table(
        'app_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )


def downgrade() -> None:
    op.drop_table('app_settings')
    op.drop_table('profile_info')
    op.drop_index('ix_expenses_category', 'expenses')
    op.drop_index('ix_expenses_date', 'expenses')
    op.drop_table('expenses')
    op.drop_index('ix_time_entries_date', 'time_entries')
    op.drop_table('time_entries')
    op.drop_table('payments')
    op.drop_table('invoice_items')
    op.drop_index('ix_invoices_issue_date', 'invoices')
    op.drop_index('ix_invoices_status', 'invoices')
    op.drop_table('invoices')
    op.drop_index('ix_quote_requests_status', 'quote_requests')
    op.drop_table('quote_requests')
    op.drop_table('project_assets')
    op.drop_table('project_technologies')
    op.drop_index('ix_projects_is_public', 'projects')
    op.drop_index('ix_projects_status', 'projects')
    op.drop_table('projects')
    op.drop_table('technologies')
    op.drop_index('ix_clients_rfc', 'clients')
    op.drop_index('ix_clients_email', 'clients')
    op.drop_table('clients')