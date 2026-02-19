from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import BlogPost, FloorPlan, Portfolio, PortfolioImage
from app.schemas.admin import (
    AdminBlogPostCreate,
    AdminBlogPostUpdate,
    AdminPortfolioCreate,
    AdminPortfolioUpdate,
    PublishStatus,
)


def _maybe_mark_portfolio_published(row: Portfolio, status: PublishStatus) -> None:
    if status == PublishStatus.published and row.published_at is None:
        row.published_at = datetime.now(UTC)
    if status != PublishStatus.published:
        row.published_at = None


def create_admin_portfolio(db: Session, payload: AdminPortfolioCreate) -> Portfolio:
    data = payload.model_dump()
    unit_floorplan_url = data.pop("unit_floorplan_url", None)
    before_image_url = data.pop("before_image_url", None)
    after_image_url = data.pop("after_image_url", None)
    before_area_label = data.pop("before_area_label", None)
    after_area_label = data.pop("after_area_label", None)
    before_floorplan_x = data.pop("before_floorplan_x", None)
    before_floorplan_y = data.pop("before_floorplan_y", None)
    after_floorplan_x = data.pop("after_floorplan_x", None)
    after_floorplan_y = data.pop("after_floorplan_y", None)
    before_image_items = data.pop("before_image_items", None) or []
    after_image_items = data.pop("after_image_items", None) or []

    row = Portfolio(**data)
    _maybe_mark_portfolio_published(row, payload.status)
    db.add(row)
    db.commit()
    db.refresh(row)

    next_image_id = db.execute(select(func.coalesce(func.max(PortfolioImage.id), 0))).scalar_one() + 1
    images: list[PortfolioImage] = []

    if before_image_items:
        for item in before_image_items:
            images.append(
                PortfolioImage(
                    id=next_image_id,
                    portfolio_id=row.id,
                    kind="before",
                    image_url=item["image_url"],
                    sort_order=item.get("sort_order", 1),
                    area_label=item.get("area_label"),
                    floorplan_x=item.get("floorplan_x"),
                    floorplan_y=item.get("floorplan_y"),
                )
            )
            next_image_id += 1
    elif before_image_url:
        images.append(
            PortfolioImage(
                id=next_image_id,
                portfolio_id=row.id,
                kind="before",
                image_url=before_image_url,
                sort_order=1,
                area_label=before_area_label,
                floorplan_x=before_floorplan_x,
                floorplan_y=before_floorplan_y,
            )
        )
        next_image_id += 1

    if after_image_items:
        for item in after_image_items:
            images.append(
                PortfolioImage(
                    id=next_image_id,
                    portfolio_id=row.id,
                    kind="after",
                    image_url=item["image_url"],
                    sort_order=item.get("sort_order", 1),
                    area_label=item.get("area_label"),
                    floorplan_x=item.get("floorplan_x"),
                    floorplan_y=item.get("floorplan_y"),
                )
            )
            next_image_id += 1
    elif after_image_url:
        images.append(
            PortfolioImage(
                id=next_image_id,
                portfolio_id=row.id,
                kind="after",
                image_url=after_image_url,
                sort_order=1,
                area_label=after_area_label,
                floorplan_x=after_floorplan_x,
                floorplan_y=after_floorplan_y,
            )
        )

    if images:
        db.add_all(images)
        db.commit()

    if unit_floorplan_url:
        floor_plan = db.execute(
            select(FloorPlan).where(FloorPlan.unit_type_id == row.unit_type_id).order_by(FloorPlan.id.asc())
        ).scalars().first()
        if floor_plan is None:
            next_floorplan_id = db.execute(select(func.coalesce(func.max(FloorPlan.id), 0))).scalar_one() + 1
            floor_plan = FloorPlan(
                id=next_floorplan_id,
                unit_type_id=row.unit_type_id,
                image_url=unit_floorplan_url,
                structure_tags=None,
                embedding=None,
            )
            db.add(floor_plan)
        else:
            floor_plan.image_url = unit_floorplan_url
        db.commit()

    return row


def list_admin_portfolios(
    db: Session,
    vendor_id: int | None = None,
    status: PublishStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Portfolio]:
    stmt = select(Portfolio)
    if vendor_id is not None:
        stmt = stmt.where(Portfolio.vendor_id == vendor_id)
    if status is not None:
        stmt = stmt.where(Portfolio.status == status.value)

    rows = db.execute(
        stmt.order_by(Portfolio.created_at.desc(), Portfolio.id.desc()).limit(limit).offset(offset)
    ).scalars()
    return list(rows)


def update_admin_portfolio(db: Session, portfolio_id: int, payload: AdminPortfolioUpdate) -> Portfolio | None:
    row = db.get(Portfolio, portfolio_id)
    if row is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(row, key, value)

    if payload.status is not None:
        _maybe_mark_portfolio_published(row, payload.status)

    db.commit()
    db.refresh(row)
    return row


def _maybe_mark_blog_published(row: BlogPost, status: PublishStatus) -> None:
    if status == PublishStatus.published and row.published_at is None:
        row.published_at = datetime.now(UTC)
    if status != PublishStatus.published:
        row.published_at = None


def create_blog_post(db: Session, payload: AdminBlogPostCreate) -> BlogPost:
    row = BlogPost(**payload.model_dump())
    _maybe_mark_blog_published(row, payload.status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_blog_posts(
    db: Session,
    vendor_id: int | None = None,
    status: PublishStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[BlogPost]:
    stmt = select(BlogPost)
    if vendor_id is not None:
        stmt = stmt.where(BlogPost.vendor_id == vendor_id)
    if status is not None:
        stmt = stmt.where(BlogPost.status == status.value)

    rows = db.execute(stmt.order_by(BlogPost.created_at.desc(), BlogPost.id.desc()).limit(limit).offset(offset)).scalars()
    return list(rows)


def update_blog_post(db: Session, post_id: int, payload: AdminBlogPostUpdate) -> BlogPost | None:
    row = db.get(BlogPost, post_id)
    if row is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(row, key, value)

    if payload.status is not None:
        _maybe_mark_blog_published(row, payload.status)

    db.commit()
    db.refresh(row)
    return row
