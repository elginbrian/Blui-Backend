"""Fix transaction columns

Revision ID: 002_fix_transaction_columns
Revises: 001_initial
Create Date: 2025-11-20 00:00:00.000000

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '002_fix_transaction_columns'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename description to name
    op.alter_column('transactions', 'description', new_column_name='name')
    # Add note column
    op.add_column('transactions', sa.Column('note', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove note column
    op.drop_column('transactions', 'note')
    # Rename name back to description
    op.alter_column('transactions', 'name', new_column_name='description')