"""Add user language column

Revision ID: 002_add_user_language
Revises: 001_initial_schema
Create Date: 2026-09-07 22:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_user_language'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('language', sa.String(length=10), server_default='ru', nullable=False))

def downgrade() -> None:
    op.drop_column('users', 'language')
