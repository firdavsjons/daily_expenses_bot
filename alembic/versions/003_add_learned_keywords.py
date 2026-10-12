"""Add learned keywords

Revision ID: 003_add_learned_keywords
Revises: 002_add_user_language
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_add_learned_keywords"
down_revision: Union[str, None] = "002_add_user_language"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learned_keywords",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=100), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learned_keywords_user_keyword", "learned_keywords", ["user_id", "keyword"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_learned_keywords_user_keyword", table_name="learned_keywords")
    op.drop_table("learned_keywords")