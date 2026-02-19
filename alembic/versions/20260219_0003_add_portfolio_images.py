"""add portfolio images table

Revision ID: 20260219_0003
Revises: 20260219_0002
Create Date: 2026-02-19 22:50:00
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0003"
down_revision: Union[str, Sequence[str], None] = "20260219_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio_images (
          id BIGINT PRIMARY KEY,
          portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
          kind VARCHAR(20) NOT NULL,
          image_url VARCHAR(500) NOT NULL,
          sort_order INT NOT NULL DEFAULT 0,
          caption VARCHAR(200),
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_portfolio_images_portfolio ON portfolio_images (portfolio_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_portfolio_images_kind_sort ON portfolio_images (kind, sort_order)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_portfolio_images_kind_sort")
    op.execute("DROP INDEX IF EXISTS ix_portfolio_images_portfolio")
    op.execute("DROP TABLE IF EXISTS portfolio_images")
