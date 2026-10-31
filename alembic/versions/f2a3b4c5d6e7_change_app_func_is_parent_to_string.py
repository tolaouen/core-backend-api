"""change app_func is_parent to string

Revision ID: f2a3b4c5d6e7
Revises: e8a1b2c3d4e5
Create Date: 2026-10-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e8a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"]: column for column in sa.inspect(op.get_bind()).get_columns("app_func")}
    is_parent = columns.get("is_parent")

    if is_parent and isinstance(is_parent["type"], sa.Boolean):
        op.alter_column(
            "app_func",
            "is_parent",
            existing_type=sa.Boolean(),
            type_=sa.String(length=255),
            existing_nullable=is_parent["nullable"],
            postgresql_using=(
                "CASE WHEN is_parent IS NULL THEN NULL "
                "WHEN is_parent THEN 'Parent' ELSE 'Child' END"
            ),
        )


def downgrade() -> None:
    columns = {column["name"]: column for column in sa.inspect(op.get_bind()).get_columns("app_func")}
    is_parent = columns.get("is_parent")

    if is_parent and isinstance(is_parent["type"], sa.String):
        op.alter_column(
            "app_func",
            "is_parent",
            existing_type=sa.String(length=255),
            type_=sa.Boolean(),
            existing_nullable=is_parent["nullable"],
            postgresql_using=(
                "CASE WHEN is_parent IS NULL THEN NULL "
                "WHEN lower(is_parent) IN ('parent', 'true', '1') THEN TRUE "
                "ELSE FALSE END"
            ),
        )