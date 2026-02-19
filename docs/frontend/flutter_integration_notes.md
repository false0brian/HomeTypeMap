# Flutter Integration Notes

## API 호출 순서
1. 지도 bounds 변경: `GET /api/v1/map/pins`
2. 단지 핀 탭: `GET /api/v1/complexes/{complex_id}`
3. 타입 칩 탭: `GET /api/v1/complexes/{complex_id}/portfolios?unit_type_id=...`
4. 카드 저장: `POST /api/v1/favorites`
5. 업체 문의: `POST /api/v1/quote-requests`

## 권장 상태 구조
- `MapState`: bounds, zoom, clusters, complexPins
- `BottomSheetState`: selectedComplex, unitTypes, selectedUnitType
- `PortfolioState`: filters, list, total, loading, pagination

## 모델 생성
- `python scripts/export_openapi.py`로 `docs/openapi.json` 생성
- `openapi-generator` 또는 `swagger_dart_code_generator`로 Dart 모델 생성

## 주의점
- `work_scope`는 enum 문자열: `kitchen`, `bathroom`, `partial`, `full_remodeling`
- `zoom <= 11`에서는 `clusters`만 올 수 있음
- `zoom >= 12`에서는 `complexes`만 올 수 있음
