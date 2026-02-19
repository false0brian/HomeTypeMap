from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.map import MapBoundsQuery, MapPinsResponse
from app.schemas.portfolio import (
    ComplexDetailResponse,
    FavoriteCreateRequest,
    FavoriteResponse,
    PortfolioFilterQuery,
    PortfolioListResponse,
    WorkScopeType,
)
from app.schemas.vendor import QuoteRequestCreate, QuoteRequestResponse
from app.services.favorite_service import create_favorite, list_favorites
from app.services.map_service import get_map_pins
from app.services.portfolio_service import get_complex_detail, list_portfolios
from app.services.quote_service import create_quote_request

router = APIRouter(prefix="/api/v1")


@router.get(
    "/map/pins",
    response_model=MapPinsResponse,
    tags=["map"],
    summary="지도 범위 내 단지 핀 또는 클러스터 조회",
)
def map_pins(
    south: float = Query(..., description="지도 하단 위도", examples=[37.4]),
    west: float = Query(..., description="지도 좌측 경도", examples=[127.0]),
    north: float = Query(..., description="지도 상단 위도", examples=[37.6]),
    east: float = Query(..., description="지도 우측 경도", examples=[127.2]),
    zoom: int = Query(..., ge=0, le=22, description="클라이언트 지도 줌 레벨", examples=[13]),
    db: Session = Depends(get_db),
):
    bounds = MapBoundsQuery(south=south, west=west, north=north, east=east, zoom=zoom)
    return get_map_pins(db, bounds)


@router.get(
    "/complexes/{complex_id}",
    response_model=ComplexDetailResponse,
    tags=["complex"],
    summary="단지 상세와 평형 타입 칩 조회",
)
def complex_detail(complex_id: int, db: Session = Depends(get_db)):
    detail = get_complex_detail(db, complex_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="complex not found")
    return detail


@router.get(
    "/complexes/{complex_id}/portfolios",
    response_model=PortfolioListResponse,
    tags=["complex"],
    summary="타입별 포트폴리오 리스트 조회",
)
def complex_portfolios(
    complex_id: int,
    unit_type_id: int | None = Query(default=None, description="평형 타입 ID", examples=[1001]),
    min_area: float | None = Query(default=None, ge=0, description="전용면적 최소(m2)", examples=[59]),
    max_area: float | None = Query(default=None, ge=0, description="전용면적 최대(m2)", examples=[84]),
    budget_min_krw: int | None = Query(default=None, ge=0, description="예산 하한(원)", examples=[30000000]),
    budget_max_krw: int | None = Query(default=None, ge=0, description="예산 상한(원)", examples=[50000000]),
    work_scope: WorkScopeType | None = Query(default=None, description="공사 범위"),
    style: str | None = Query(default=None, description="스타일 키워드", examples=["minimal"]),
    limit: int = Query(default=30, ge=1, le=100, description="페이지 크기"),
    offset: int = Query(default=0, ge=0, description="페이지 오프셋"),
    db: Session = Depends(get_db),
):
    filters = PortfolioFilterQuery(
        min_area=min_area,
        max_area=max_area,
        budget_min_krw=budget_min_krw,
        budget_max_krw=budget_max_krw,
        work_scope=work_scope,
        style=style,
        limit=limit,
        offset=offset,
    )
    return list_portfolios(db, complex_id=complex_id, unit_type_id=unit_type_id, query=filters)


@router.post(
    "/favorites",
    response_model=FavoriteResponse,
    status_code=201,
    tags=["favorite"],
    summary="포트폴리오 즐겨찾기 저장",
)
def favorite_create(payload: FavoriteCreateRequest, db: Session = Depends(get_db)):
    row = create_favorite(db, user_key=payload.user_key, portfolio_id=payload.portfolio_id)
    return FavoriteResponse(favorite_id=row.id, user_key=row.user_key, portfolio_id=row.portfolio_id)


@router.get(
    "/favorites",
    response_model=list[FavoriteResponse],
    tags=["favorite"],
    summary="사용자 즐겨찾기 조회",
)
def favorite_list(user_key: str = Query(...), db: Session = Depends(get_db)):
    rows = list_favorites(db, user_key=user_key)
    return [
        FavoriteResponse(favorite_id=row.id, user_key=row.user_key, portfolio_id=row.portfolio_id)
        for row in rows
    ]


@router.post(
    "/quote-requests",
    response_model=QuoteRequestResponse,
    status_code=201,
    tags=["quote"],
    summary="업체 문의/견적 요청 생성",
)
def quote_request_create(payload: QuoteRequestCreate, db: Session = Depends(get_db)):
    row = create_quote_request(
        db,
        user_key=payload.user_key,
        vendor_id=payload.vendor_id,
        portfolio_id=payload.portfolio_id,
        preferred_date=payload.preferred_date,
        message=payload.message,
    )
    return QuoteRequestResponse(
        quote_request_id=row.id,
        user_key=row.user_key,
        vendor_id=row.vendor_id,
        portfolio_id=row.portfolio_id,
    )
