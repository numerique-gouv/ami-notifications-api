"""Extract Registration.email to User table

Revision ID: f816eeeca5cd
Revises:
Create Date: 2025-05-19 15:10:18.386181

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f816eeeca5cd"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the `ami_user` table.
    op.create_table(
        "ami_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create a user entry in the `ami_user` table for each existing registration.
    op.execute("""
       INSERT INTO ami_user (email)
       SELECT DISTINCT email FROM registration
    """)

    # Add the `registration.user_id` column, nullable for now.
    op.add_column("registration", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_registration_user_id_ami_user", "registration", "ami_user", ["user_id"], ["id"]
    )
    # Update the `registration.user_id` column from the `ami_user` table.
    op.execute("""
        UPDATE registration
        SET user_id = (
            SELECT id
            FROM ami_user
            WHERE registration.email = ami_user.email)
    """)
    # Set the `registration.user_id` column to be not nullable.
    op.alter_column("registration", "user_id", nullable=False)
    op.drop_column("registration", "email")

    # Add the `notification.user_id` column, nullable for now.
    op.add_column("notification", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_notification_user_id_ami_user", "notification", "ami_user", ["user_id"], ["id"]
    )
    # Update the `notification.user_id` column from the `ami_user` table.
    op.execute("""
        UPDATE notification
        SET user_id = (
            SELECT id
            FROM ami_user
            WHERE notification.email = ami_user.email)
    """)
    # Set the `notification.user_id` column to be not nullable.
    op.alter_column("notification", "user_id", nullable=False)
    op.drop_column("notification", "email")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "registration", sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    # Update the `registration.email` column from the `ami_user` table.
    op.execute("""
        UPDATE registration
        SET email = (
            SELECT email
            FROM ami_user
            WHERE registration.user_id = ami_user.id)
    """)
    op.alter_column("registration", "user_id", nullable=False)
    op.drop_constraint("fk_registration_user_id_ami_user", "registration", type_="foreignkey")
    op.drop_column("registration", "user_id")

    op.add_column(
        "notification", sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    # Update the `notification.email` column from the `ami_user` table.
    op.execute("""
        UPDATE notification
        SET email = (
            SELECT email
            FROM ami_user
            WHERE notification.user_id = ami_user.id)
    """)
    op.alter_column("notification", "user_id", nullable=False)
    op.drop_constraint("fk_notification_user_id_ami_user", "notification", type_="foreignkey")
    op.drop_column("notification", "user_id")

    # Drop the User table that was automatically created with SQLModel.metadata.create_all
    op.drop_table("ami_user")
