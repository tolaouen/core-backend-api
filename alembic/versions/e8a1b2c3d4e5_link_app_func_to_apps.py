"""link app_func to apps

Revision ID: e8a1b2c3d4e5
Revises: d6f7a8b9c0d1
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "d6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = {col["name"] for col in inspector.get_columns("app_func")}

    if "app_id" not in columns:
        op.add_column("app_func", sa.Column("app_id", sa.Integer(), nullable=True))

    # Insert missing apps from app_func if any
    connection.execute(
        sa.text(
            """
            INSERT INTO apps (name, base_url, app_code, status)
            SELECT DISTINCT app_code, '', app_code, 'ACT'
            FROM app_func
            WHERE app_code NOT IN (SELECT app_code FROM apps WHERE app_code IS NOT NULL)
              AND app_code IS NOT NULL
            """
        )
    )

    # Populate app_id from apps table matching app_code
    connection.execute(
        sa.text(
            """
            UPDATE app_func AS af
            SET app_id = apps.id
            FROM apps
            WHERE apps.app_code = af.app_code
              AND af.app_id IS NULL
            """
        )
    )

    op.alter_column("app_func", "app_id", nullable=False)

    foreign_keys = inspector.get_foreign_keys("app_func")
    has_app_fk = any(
        fk.get("constrained_columns") == ["app_id"]
        and fk.get("referred_table") == "apps"
        for fk in foreign_keys
    )
    if not has_app_fk:
        op.create_foreign_key(
            "fk_app_func_app_id_apps",
            "app_func",
            "apps",
            ["app_id"],
            ["id"],
            ondelete="CASCADE",
        )

    indexes = {idx["name"] for idx in inspector.get_indexes("app_func")}
    if "ix_app_func_app_id" not in indexes:
        op.create_index(op.f("ix_app_func_app_id"), "app_func", ["app_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_app_func_app_id"), table_name="app_func")
    op.drop_constraint("fk_app_func_app_id_apps", "app_func", type_="foreignkey")
    op.drop_column("app_func", "app_id")
