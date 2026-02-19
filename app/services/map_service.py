from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Complex, Portfolio
from app.schemas.map import ClusterPin, ComplexPin, MapBoundsQuery, MapPinsResponse


def _bbox_base_query(bounds: MapBoundsQuery) -> Select:
    return (
        select(Complex)
        .where(Complex.centroid_latitude >= bounds.south)
        .where(Complex.centroid_latitude <= bounds.north)
        .where(Complex.centroid_longitude >= bounds.west)
        .where(Complex.centroid_longitude <= bounds.east)
    )


def get_map_pins(db: Session, bounds: MapBoundsQuery) -> MapPinsResponse:
    if bounds.zoom <= 11:
        precision = 2 if bounds.zoom <= 8 else 3
        lat_bucket = func.round(Complex.centroid_latitude, precision)
        lng_bucket = func.round(Complex.centroid_longitude, precision)

        rows = db.execute(
            select(
                lat_bucket.label("lat_bucket"),
                lng_bucket.label("lng_bucket"),
                func.count(Complex.id).label("count"),
            )
            .select_from(Complex)
            .where(Complex.centroid_latitude >= bounds.south)
            .where(Complex.centroid_latitude <= bounds.north)
            .where(Complex.centroid_longitude >= bounds.west)
            .where(Complex.centroid_longitude <= bounds.east)
            .group_by(lat_bucket, lng_bucket)
            .order_by(func.count(Complex.id).desc())
            .limit(300)
        ).all()

        return MapPinsResponse(
            clusters=[
                ClusterPin(
                    cluster_key=f"{row.lat_bucket}:{row.lng_bucket}",
                    center_latitude=row.lat_bucket,
                    center_longitude=row.lng_bucket,
                    count=row.count,
                )
                for row in rows
            ],
            complexes=[],
        )

    rows = db.execute(
        select(
            Complex.id,
            Complex.name,
            Complex.centroid_latitude,
            Complex.centroid_longitude,
            func.count(Portfolio.id).label("portfolio_count"),
        )
        .outerjoin(Portfolio, Portfolio.complex_id == Complex.id)
        .where(Complex.centroid_latitude >= bounds.south)
        .where(Complex.centroid_latitude <= bounds.north)
        .where(Complex.centroid_longitude >= bounds.west)
        .where(Complex.centroid_longitude <= bounds.east)
        .group_by(Complex.id)
        .order_by(func.count(Portfolio.id).desc(), Complex.id)
        .limit(1000)
    ).all()

    return MapPinsResponse(
        clusters=[],
        complexes=[
            ComplexPin(
                complex_id=row.id,
                name=row.name,
                latitude=row.centroid_latitude,
                longitude=row.centroid_longitude,
                portfolio_count=row.portfolio_count,
            )
            for row in rows
        ],
    )
