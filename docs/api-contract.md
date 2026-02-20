# API Contract (MVP v1)

Base URL: `/api/v1`

## 1) 지도 핀/클러스터
`GET /map/pins?south={}&west={}&north={}&east={}&zoom={}`

- `zoom <= 11`: `clusters` 반환
- `zoom >= 12`: `complexes` 반환

응답 예시:
```json
{
  "clusters": [
    {
      "cluster_key": "37.49:127.10",
      "center_latitude": 37.49,
      "center_longitude": 127.10,
      "count": 24
    }
  ],
  "complexes": []
}
```

### 현재 위치 기준 근처 검색
`GET /map/nearby?lat={}&lng={}&radius_m={}`

- 기본 반경: `3000` (m)
- 거리 오름차순 반환

응답 예시:
```json
{
  "center_latitude": 37.49,
  "center_longitude": 127.10,
  "radius_m": 3000,
  "items": [
    {
      "complex_id": 101,
      "name": "분당 샘플자이",
      "latitude": 37.4875,
      "longitude": 127.1022,
      "portfolio_count": 2,
      "distance_m": 420.5
    }
  ]
}
```

## 2) 단지 상세 + 타입 칩
`GET /complexes/{complex_id}`

응답 예시:
```json
{
  "complex_id": 101,
  "name": "분당 샘플자이",
  "address": "경기도 성남시 분당구 정자동 100",
  "built_year": 2012,
  "household_count": 1240,
  "unit_types": [
    {
      "unit_type_id": 1001,
      "exclusive_area_m2": 59.95,
      "type_code": "A",
      "room_count": 3,
      "bathroom_count": 2,
      "structure_keyword": "판상형",
      "portfolio_count": 12
    }
  ]
}
```

## 3) 타입별 포트폴리오 + 필터
`GET /complexes/{complex_id}/portfolios`

쿼리:
- `unit_type_id`
- `min_area`, `max_area`
- `budget_min_krw`, `budget_max_krw`
- `work_scope`: `kitchen | bathroom | partial | full_remodeling`
- `style`
- `limit`, `offset`

응답 예시:
```json
{
  "items": [
    {
      "portfolio_id": 9001,
      "title": "59A 미니멀 화이트 리모델링",
      "before_image_url": "https://...",
      "after_image_url": "https://...",
      "work_scope": "full_remodeling",
      "style": "minimal",
      "budget_min_krw": 35000000,
      "budget_max_krw": 45000000,
      "duration_days": 28,
      "vendor_id": 501,
      "vendor_name": "샘플 인테리어"
    }
  ],
  "total": 1
}
```

## 4) 즐겨찾기
- `POST /favorites`
- `GET /favorites?user_key={}`

## 5) 견적 요청
- `POST /quote-requests`
- `vendor_id` 또는 `portfolio_id` 중 최소 1개 필요

## 6) 관리자 CMS API
- 공통 헤더: `X-Admin-Key: {ADMIN_API_KEY}`
- 포트폴리오
  - `GET /admin/portfolios`
  - `POST /admin/portfolios`
  - `PATCH /admin/portfolios/{portfolio_id}`
- 블로그
  - `GET /admin/blog-posts`
  - `POST /admin/blog-posts`
  - `PATCH /admin/blog-posts/{post_id}`

`status` 값:
- `draft`
- `review`
- `published`

## 프론트 타입 생성
- OpenAPI 덤프: `python scripts/export_openapi.py`
- TypeScript 예시: `npx openapi-typescript docs/openapi.json -o src/api-types.ts`
- Flutter(Dart) 예시: `dart run build_runner build` 기반 생성 도구에서 `docs/openapi.json` 사용

## API 버전 정책
- 현재 안정 버전: `v1` (`/api/v1`)
- 호환성 원칙:
  - `v1`에서 기존 필드는 삭제/의미변경하지 않는다.
  - 새 기능은 optional 필드 추가 또는 새 엔드포인트로 확장한다.
  - breaking change가 필요하면 `v2`를 새 base path(`/api/v2`)로 추가한다.
- 운영 절차:
  - PR에 `API Change` 섹션으로 변경 타입(`non-breaking`/`breaking`)을 명시한다.
  - `breaking`은 최소 1개 릴리스 주기 동안 `v1` 병행 운영 계획을 함께 제출한다.
