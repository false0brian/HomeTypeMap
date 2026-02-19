from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models import Complex, Portfolio, PortfolioImage, UnitType, Vendor
from app.schemas.portfolio import (
    ComplexDetailResponse,
    PortfolioCard,
    PortfolioFilterQuery,
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
            func.count(Portfolio.id).label("portfolio_count"),
        )
        .outerjoin(Portfolio, Portfolio.unit_type_id == UnitType.id)
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
        )
        .select_from(Portfolio)
        .join(UnitType, UnitType.id == Portfolio.unit_type_id)
        .outerjoin(Vendor, Vendor.id == Portfolio.vendor_id)
        .where(and_(*conditions))
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
            )
            .where(PortfolioImage.portfolio_id.in_(portfolio_ids))
            .where(PortfolioImage.kind.in_(["before", "after"]))
            .order_by(PortfolioImage.sort_order.asc(), PortfolioImage.id.asc())
        ).all()

    image_map: dict[int, dict[str, list[str]]] = {}
    for row in image_rows:
        image_map.setdefault(row.portfolio_id, {"before": [], "after": []})
        image_map[row.portfolio_id][row.kind].append(row.image_url)

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
                before_images=image_map.get(row.id, {}).get("before", []),
                after_images=image_map.get(row.id, {}).get("after", []),
            )
            for row in rows
        ],
    )
