"""allow duplicate app codes

Revision ID: d6f7a8b9c0d1
Revises: c5e6f7a8b9c0
Create Date: 2026-09-14

"""
from typing import Sequence, Union

from alembic import op


revision: str = "d6f7a8b9c0d1"
down_revision: Union[str, Sequence[str], None] = "c5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("apps_app_code_key", "apps", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("apps_app_code_key", "apps", ["app_code"])
