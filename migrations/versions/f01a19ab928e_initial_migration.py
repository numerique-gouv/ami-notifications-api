"""Initial migration

Revision ID: f01a19ab928e
Revises:
Create Date: 2025-06-02 15:41:18.526337

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f01a19ab928e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("email", sa.VARCHAR(), nullable=False),
        sa.Column("message", sa.VARCHAR(), nullable=False),
        sa.Column("sender", sa.VARCHAR(), nullable=True),
        sa.Column("title", sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "registration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.VARCHAR(), nullable=False),
        sa.Column("subscription", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("registration")
    op.drop_table("notification")
