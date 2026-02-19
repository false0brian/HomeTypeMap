from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models import Complex, FloorPlan, Portfolio, PortfolioImage, UnitType, Vendor
from app.schemas.portfolio import (
    ComplexDetailResponse,
    PortfolioCard,
    PortfolioFilterQuery,
    PortfolioImageItem,
    PortfolioListResponse,
    UnitTypeChip,
)


def get_complex_detail(db: Session, complex_id: int) -> ComplexDetailResponse | None:
    complex_row = db.get(Complex, complex_id)
    if complex_row is None:
        return None

    type_rows = db.execute(
        select(
            UnitType.id,
            UnitType.exclusive_area_m2,
            UnitType.type_code,
            UnitType.room_count,
            UnitType.bathroom_count,
            UnitType.structure_keyword,
            func.min(FloorPlan.image_url).label("representative_floor_plan_url"),
            func.count(Portfolio.id).label("portfolio_count"),
        )
        .outerjoin(Portfolio, Portfolio.unit_type_id == UnitType.id)
        .outerjoin(FloorPlan, FloorPlan.unit_type_id == UnitType.id)
        .where(UnitType.complex_id == complex_id)
        .group_by(UnitType.id)
        .order_by(UnitType.exclusive_area_m2.asc(), UnitType.type_code.asc())
    ).all()

    return ComplexDetailResponse(
        complex_id=complex_row.id,
        name=complex_row.name,
        address=complex_row.address,
        built_year=complex_row.built_year,
        household_count=complex_row.household_count,
        unit_types=[
            UnitTypeChip(
                unit_type_id=row.id,
                exclusive_area_m2=row.exclusive_area_m2,
                type_code=row.type_code,
                room_count=row.room_count,
                bathroom_count=row.bathroom_count,
                structure_keyword=row.structure_keyword,
                representative_floor_plan_url=row.representative_floor_plan_url,
                portfolio_count=row.portfolio_count,
            )
            for row in type_rows
        ],
    )


def list_portfolios(
    db: Session,
    complex_id: int,
    unit_type_id: int | None,
    query: PortfolioFilterQuery,
) -> PortfolioListResponse:
    conditions = [Portfolio.complex_id == complex_id]

    if unit_type_id is not None:
        conditions.append(Portfolio.unit_type_id == unit_type_id)

    if query.min_area is not None:
        conditions.append(UnitType.exclusive_area_m2 >= query.min_area)
    if query.max_area is not None:
        conditions.append(UnitType.exclusive_area_m2 <= query.max_area)
    if query.budget_min_krw is not None:
        conditions.append(Portfolio.budget_max_krw >= query.budget_min_krw)
    if query.budget_max_krw is not None:
        conditions.append(Portfolio.budget_min_krw <= query.budget_max_krw)
    if query.work_scope is not None:
        conditions.append(Portfolio.work_scope == query.work_scope)
    if query.style is not None:
        conditions.append(Portfolio.style == query.style)

    base_stmt = (
        select(
            Portfolio.id,
            Portfolio.title,
            Portfolio.before_image_url,
            Portfolio.after_image_url,
            Portfolio.work_scope,
            Portfolio.style,
            Portfolio.budget_min_krw,
            Portfolio.budget_max_krw,
            Portfolio.duration_days,
            Vendor.id.label("vendor_id"),
            Vendor.name.label("vendor_name"),
            func.min(FloorPlan.image_url).label("unit_type_floor_plan_url"),
        )
        .select_from(Portfolio)
        .join(UnitType, UnitType.id == Portfolio.unit_type_id)
        .outerjoin(FloorPlan, FloorPlan.unit_type_id == UnitType.id)
        .outerjoin(Vendor, Vendor.id == Portfolio.vendor_id)
        .where(and_(*conditions))
        .group_by(Portfolio.id, Vendor.id)
    )

    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    rows = db.execute(
        base_stmt
        .order_by(Portfolio.created_at.desc(), Portfolio.id.desc())
        .limit(query.limit)
        .offset(query.offset)
    ).all()

    portfolio_ids = [row.id for row in rows]
    image_rows = []
    if portfolio_ids:
        image_rows = db.execute(
            select(
                PortfolioImage.portfolio_id,
                PortfolioImage.kind,
                PortfolioImage.image_url,
                PortfolioImage.sort_order,
                PortfolioImage.caption,
                PortfolioImage.area_label,
                PortfolioImage.floorplan_x,
                PortfolioImage.floorplan_y,
            )
            .where(PortfolioImage.portfolio_id.in_(portfolio_ids))
            .where(PortfolioImage.kind.in_(["before", "after"]))
            .order_by(PortfolioImage.sort_order.asc(), PortfolioImage.id.asc())
        ).all()

    image_map: dict[int, dict[str, list[PortfolioImageItem]]] = {}
    for row in image_rows:
        image_map.setdefault(row.portfolio_id, {"before": [], "after": []})
        image_map[row.portfolio_id][row.kind].append(
            PortfolioImageItem(
                image_url=row.image_url,
                sort_order=row.sort_order,
                caption=row.caption,
                area_label=row.area_label,
                floorplan_x=row.floorplan_x,
                floorplan_y=row.floorplan_y,
            )
        )

    return PortfolioListResponse(
        total=total,
        items=[
            PortfolioCard(
                portfolio_id=row.id,
                title=row.title,
                before_image_url=row.before_image_url,
                after_image_url=row.after_image_url,
                work_scope=row.work_scope,
                style=row.style,
                budget_min_krw=row.budget_min_krw,
                budget_max_krw=row.budget_max_krw,
                duration_days=row.duration_days,
                vendor_id=row.vendor_id,
                vendor_name=row.vendor_name,
                unit_type_floor_plan_url=row.unit_type_floor_plan_url,
                before_images=image_map.get(row.id, {}).get("before", []),
                after_images=image_map.get(row.id, {}).get("after", []),
            )
            for row in rows
        ],
    )
