"""create apps table and link user_app

Revision ID: b4d8e2f6a1c3
Revises: 9c1e2f4a6b7d
Create Date: 2026-09-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4d8e2f6a1c3"
down_revision: Union[str, Sequence[str], None] = "7a35b7fd3c4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "apps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=255), nullable=False),
        sa.Column("app_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["permission_id"], ["app_permissions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("app_code"),
    )
    op.create_index(op.f("ix_apps_id"), "apps", ["id"], unique=False)

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO apps (name, base_url, app_code, status)
            SELECT DISTINCT app_code, '', app_code, 'ACT'
            FROM user_app
            """
        )
    )

    op.add_column("user_app", sa.Column("app_id", sa.Integer(), nullable=True))
    connection.execute(
        sa.text(
            """
            UPDATE user_app AS ua
            SET app_id = apps.id
            FROM apps
            WHERE apps.app_code = ua.app_code
            """
        )
    )
    op.alter_column("user_app", "app_id", nullable=False)
    op.create_foreign_key(
        "fk_user_app_app_id_apps",
        "user_app",
        "apps",
        ["app_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_user_app_app_id"), "user_app", ["app_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_app_app_id"), table_name="user_app")
    op.drop_constraint("fk_user_app_app_id_apps", "user_app", type_="foreignkey")
    op.drop_column("user_app", "app_id")
    op.drop_index(op.f("ix_apps_id"), table_name="apps")
    op.drop_table("apps")
