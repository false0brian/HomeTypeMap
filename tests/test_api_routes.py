import app.api.routes as routes


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_map_pins_returns_service_payload(client, monkeypatch) -> None:
    expected = {
        "clusters": [
            {
                "cluster_key": "37.49:127.10",
                "center_latitude": 37.49,
                "center_longitude": 127.10,
                "count": 12,
            }
        ],
        "complexes": [],
    }

    monkeypatch.setattr(routes, "get_map_pins", lambda db, bounds: expected)

    response = client.get("/api/v1/map/pins?south=37.4&west=127.0&north=37.6&east=127.2&zoom=10")
    assert response.status_code == 200
    assert response.json() == expected


def test_complex_detail_not_found(client, monkeypatch) -> None:
    monkeypatch.setattr(routes, "get_complex_detail", lambda db, complex_id: None)
    response = client.get("/api/v1/complexes/99999")
    assert response.status_code == 404


def test_complex_portfolios_uses_filters(client, monkeypatch) -> None:
    captured = {}

    def _fake_list(db, complex_id, unit_type_id, query):
        captured["complex_id"] = complex_id
        captured["unit_type_id"] = unit_type_id
        captured["work_scope"] = query.work_scope
        return {
            "items": [
                {
                    "portfolio_id": 1,
                    "title": "테스트",
                    "before_image_url": None,
                    "after_image_url": None,
                    "work_scope": "partial",
                    "style": "minimal",
                    "budget_min_krw": 10000000,
                    "budget_max_krw": 20000000,
                    "duration_days": 14,
                    "vendor_id": None,
                    "vendor_name": None,
                }
            ],
            "total": 1,
        }

    monkeypatch.setattr(routes, "list_portfolios", _fake_list)

    response = client.get(
        "/api/v1/complexes/101/portfolios?unit_type_id=1001&work_scope=partial&budget_min_krw=10000000"
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert captured == {"complex_id": 101, "unit_type_id": 1001, "work_scope": "partial"}


def test_complex_portfolios_rejects_invalid_work_scope(client) -> None:
    response = client.get("/api/v1/complexes/101/portfolios?work_scope=invalid_scope")
    assert response.status_code == 422


def test_favorite_create(client, monkeypatch) -> None:
    class DummyFavorite:
        id = 77
        user_key = "u-1"
        portfolio_id = 9001

    monkeypatch.setattr(routes, "create_favorite", lambda db, user_key, portfolio_id: DummyFavorite())

    response = client.post("/api/v1/favorites", json={"user_key": "u-1", "portfolio_id": 9001})
    assert response.status_code == 201
    assert response.json() == {"favorite_id": 77, "user_key": "u-1", "portfolio_id": 9001}


def test_quote_request_create(client, monkeypatch) -> None:
    class DummyQuote:
        id = 300
        user_key = "u-1"
        vendor_id = 501
        portfolio_id = None

    monkeypatch.setattr(
        routes,
        "create_quote_request",
        lambda db, user_key, vendor_id, portfolio_id, preferred_date, message: DummyQuote(),
    )

    response = client.post("/api/v1/quote-requests", json={"user_key": "u-1", "vendor_id": 501})
    assert response.status_code == 201
    assert response.json() == {"quote_request_id": 300, "user_key": "u-1", "vendor_id": 501, "portfolio_id": None}
