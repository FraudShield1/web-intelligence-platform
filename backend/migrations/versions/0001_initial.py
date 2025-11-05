"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('sites',
        sa.Column('site_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('domain', sa.String(length=255), nullable=False, unique=True),
        sa.Column('platform', sa.String(length=100)),
        sa.Column('status', sa.String(length=50), index=True),
        sa.Column('fingerprint_data', sa.JSON()),
        sa.Column('complexity_score', sa.Float()),
        sa.Column('business_value_score', sa.Float()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('last_discovered_at', sa.DateTime()),
        sa.Column('blueprint_version', sa.Integer()),
        sa.Column('notes', sa.Text()),
    )

    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(length=100), nullable=False, unique=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255)),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    op.create_table('blueprints',
        sa.Column('blueprint_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sites.site_id'), index=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('categories_data', sa.JSON()),
        sa.Column('endpoints_data', sa.JSON()),
        sa.Column('render_hints_data', sa.JSON()),
        sa.Column('selectors_data', sa.JSON()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('created_by', sa.String(length=100)),
        sa.Column('notes', sa.Text()),
    )

    op.create_table('selectors',
        sa.Column('selector_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('blueprint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('blueprints.blueprint_id'), index=True),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('css_selector', sa.String(length=500)),
        sa.Column('xpath', sa.String(length=500)),
        sa.Column('confidence', sa.Float()),
        sa.Column('generation_method', sa.String(length=50)),
        sa.Column('test_pass_rate', sa.Float()),
        sa.Column('test_count', sa.Integer()),
        sa.Column('test_failures', sa.Integer()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('last_tested_at', sa.DateTime()),
        sa.Column('notes', sa.Text()),
    )

    op.create_table('jobs',
        sa.Column('job_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sites.site_id'), index=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('method', sa.String(length=50)),
        sa.Column('status', sa.String(length=50), index=True),
        sa.Column('priority', sa.Integer()),
        sa.Column('attempt_count', sa.Integer()),
        sa.Column('max_retries', sa.Integer()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('ended_at', sa.DateTime()),
        sa.Column('error_code', sa.String(length=50)),
        sa.Column('error_message', sa.Text()),
        sa.Column('worker_id', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('payload', sa.JSON()),
        sa.Column('result', sa.JSON()),
        sa.Column('duration_seconds', sa.Integer()),
        sa.Column('heartbeat_at', sa.DateTime()),
    )

    op.create_table('analytics_metrics',
        sa.Column('metric_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sites.site_id')),
        sa.Column('date', sa.DateTime()),
        sa.Column('discovery_time_seconds', sa.Integer()),
        sa.Column('num_categories_found', sa.Integer()),
        sa.Column('num_endpoints_found', sa.Integer()),
        sa.Column('selector_failure_rate', sa.Float()),
        sa.Column('fetch_cost_usd', sa.Float()),
        sa.Column('items_extracted', sa.Integer()),
        sa.Column('method', sa.String(length=50)),
        sa.Column('job_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime()),
    )

    op.create_table('platform_templates',
        sa.Column('template_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('platform_name', sa.String(length=100), nullable=False),
        sa.Column('platform_variant', sa.String(length=100)),
        sa.Column('category_selectors', sa.JSON()),
        sa.Column('product_list_selectors', sa.JSON()),
        sa.Column('api_patterns', sa.JSON()),
        sa.Column('render_hints', sa.JSON()),
        sa.Column('confidence', sa.Float()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('match_patterns', sa.JSON()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table('platform_templates')
    op.drop_table('analytics_metrics')
    op.drop_table('jobs')
    op.drop_table('selectors')
    op.drop_table('blueprints')
    op.drop_table('users')
    op.drop_table('sites')
