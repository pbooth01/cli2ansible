"""add_tags_to_sessions

Revision ID: aca01db4e9b6
Revises:
Create Date: 2025-11-25 05:01:17.530101+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aca01db4e9b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tags column to sessions table
    op.add_column('sessions', sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'))


def downgrade() -> None:
    # Remove tags column from sessions table
    op.drop_column('sessions', 'tags')
