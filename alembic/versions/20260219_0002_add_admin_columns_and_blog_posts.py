"""add admin columns and blog posts table safely

Revision ID: 20260219_0002
Revises: 20260215_0001
Create Date: 2026-02-19 22:30:00
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0002"
down_revision: Union[str, Sequence[str], None] = "20260215_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE portfolios ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'draft'")
    op.execute("ALTER TABLE portfolios ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ")
    op.execute("CREATE INDEX IF NOT EXISTS ix_portfolios_status ON portfolios (status)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS blog_posts (
          id BIGINT PRIMARY KEY,
          vendor_id BIGINT REFERENCES vendors(id) ON DELETE SET NULL,
          title VARCHAR(220) NOT NULL,
          slug VARCHAR(140) NOT NULL UNIQUE,
          excerpt VARCHAR(500),
          content TEXT NOT NULL,
          status VARCHAR(20) NOT NULL DEFAULT 'draft',
          published_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_blog_posts_vendor_id ON blog_posts (vendor_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_blog_posts_status ON blog_posts (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_blog_posts_published_at ON blog_posts (published_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_blog_posts_published_at")
    op.execute("DROP INDEX IF EXISTS ix_blog_posts_status")
    op.execute("DROP INDEX IF EXISTS ix_blog_posts_vendor_id")
    op.execute("DROP TABLE IF EXISTS blog_posts")

    op.execute("DROP INDEX IF EXISTS ix_portfolios_status")
    op.execute("ALTER TABLE portfolios DROP COLUMN IF EXISTS published_at")
    op.execute("ALTER TABLE portfolios DROP COLUMN IF EXISTS status")
