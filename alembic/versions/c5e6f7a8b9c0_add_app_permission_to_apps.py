"""add app permission to apps

Revision ID: c5e6f7a8b9c0
Revises: b4d8e2f6a1c3
Create Date: 2026-09-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "b4d8e2f6a1c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("apps")}

    if "permission_id" not in columns:
        op.add_column(
            "apps",
            sa.Column("permission_id", sa.Integer(), nullable=True),
        )

    foreign_keys = inspector.get_foreign_keys("apps")
    has_permission_foreign_key = any(
        foreign_key.get("constrained_columns") == ["permission_id"]
        and foreign_key.get("referred_table") == "app_permissions"
        for foreign_key in foreign_keys
    )
    if not has_permission_foreign_key:
        op.create_foreign_key(
            "fk_apps_permission_id_app_permissions",
            "apps",
            "app_permissions",
            ["permission_id"],
            ["id"],
            ondelete="CASCADE",
        )

    indexes = {index["name"] for index in inspector.get_indexes("apps")}
    if "ix_apps_permission_id" not in indexes:
        op.create_index("ix_apps_permission_id", "apps", ["permission_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_apps_permission_id", table_name="apps")
