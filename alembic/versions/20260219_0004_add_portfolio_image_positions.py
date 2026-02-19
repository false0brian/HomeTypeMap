"""add position fields to portfolio images

Revision ID: 20260219_0004
Revises: 20260219_0003
Create Date: 2026-02-19 23:10:00
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0004"
down_revision: Union[str, Sequence[str], None] = "20260219_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE portfolio_images ADD COLUMN IF NOT EXISTS area_label VARCHAR(80)")
    op.execute("ALTER TABLE portfolio_images ADD COLUMN IF NOT EXISTS floorplan_x INT")
    op.execute("ALTER TABLE portfolio_images ADD COLUMN IF NOT EXISTS floorplan_y INT")


def downgrade() -> None:
    op.execute("ALTER TABLE portfolio_images DROP COLUMN IF EXISTS floorplan_y")
    op.execute("ALTER TABLE portfolio_images DROP COLUMN IF EXISTS floorplan_x")
    op.execute("ALTER TABLE portfolio_images DROP COLUMN IF EXISTS area_label")
