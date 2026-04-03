"""create job_records table

Revision ID: 0001_create_job_records
Revises: 
Create Date: 2026-04-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_job_records'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'job_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('rq_job_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('task_name', sa.String(length=255), nullable=True),
        sa.Column('enqueued_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_table('job_records')
