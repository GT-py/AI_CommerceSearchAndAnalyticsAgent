from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.db.session import SessionLocal
from app.main import app
from app.models.category import Category
from app.models.log import SearchLog
from app.models.product import Product


client = TestClient(app)

CREATED_PRODUCT_IDS: list[int] = []
CREATED_CATEGORY_IDS: list[int] = []


@pytest.fixture(autouse=True)
def cleanup_created_records():
    yield
    with SessionLocal() as db:
        if CREATED_PRODUCT_IDS:
            db.execute(delete(Product).where(Product.id.in_(CREATED_PRODUCT_IDS)))
        if CREATED_CATEGORY_IDS:
            db.execute(delete(Category).where(Category.id.in_(CREATED_CATEGORY_IDS)))
        db.commit()
    CREATED_PRODUCT_IDS.clear()
    CREATED_CATEGORY_IDS.clear()


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('admin@example.com', 'adminpass')}"}


def user_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('user@example.com', 'userpass')}"}


def first_category() -> dict:
    response = client.get("/categories")
    assert response.status_code == 200
    categories = response.json()
    assert categories
    return categories[0]


def first_product() -> dict:
    response = client.get("/products", params={"limit": 1})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    return items[0]


def product_payload(**overrides) -> dict:
    category = first_category()
    payload = {
        "name": f"Phase4 Test Product {uuid4().hex}",
        "description": "Phase 4の管理者CRUDテスト用商品です。",
        "category_id": category["id"],
        "brand": "Phase4Brand",
        "price": 12345,
        "rating": 4.1,
        "stock": 9,
        "weight_g": 500,
        "battery_hours": 10,
        "screen_size": 13.3,
        "memory_gb": 16,
        "storage_gb": 512,
        "tags": ["phase4", "crud", "test"],
    }
    payload.update(overrides)
    return payload


def create_product_as_admin(**overrides) -> dict:
    response = client.post("/admin/products", json=product_payload(**overrides), headers=admin_headers())
    assert response.status_code == 201
    product = response.json()
    CREATED_PRODUCT_IDS.append(product["id"])
    return product


def test_get_products_success() -> None:
    response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 20
    assert body["total"] >= len(body["items"])
    assert "has_next" in body


def test_get_product_detail_success() -> None:
    product = first_product()

    response = client.get(f"/products/{product['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == product["id"]


def test_search_products_by_keyword() -> None:
    response = client.get("/products", params={"keyword": "LiteBook"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert any("LiteBook" in item["name"] for item in body["items"])


def test_search_products_by_category() -> None:
    category = first_category()

    response = client.get("/products", params={"category_id": category["id"]})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(item["category"]["id"] == category["id"] for item in body["items"])


def test_search_products_by_price_range() -> None:
    response = client.get("/products", params={"min_price": 1000, "max_price": 20000, "limit": 50})

    assert response.status_code == 200
    body = response.json()
    assert body["items"]
    assert all(1000 <= item["price"] <= 20000 for item in body["items"])


def test_products_price_range_invalid_fails() -> None:
    response = client.get("/products", params={"min_price": 5000, "max_price": 1000})

    assert response.status_code == 400
    assert response.json() == {
        "detail": "min_price must be less than or equal to max_price",
    }


def test_products_pagination() -> None:
    first_page = client.get("/products", params={"page": 1, "limit": 5})
    second_page = client.get("/products", params={"page": 2, "limit": 5})

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert first_page.json()["limit"] == 5
    assert second_page.json()["page"] == 2
    assert {item["id"] for item in first_page.json()["items"]}.isdisjoint(
        {item["id"] for item in second_page.json()["items"]}
    )


def test_products_sort_price_asc() -> None:
    response = client.get("/products", params={"sort": "price_asc", "limit": 20})

    assert response.status_code == 200
    prices = [item["price"] for item in response.json()["items"]]
    assert prices == sorted(prices)


def test_create_product_by_admin_success() -> None:
    product = create_product_as_admin()

    assert product["name"].startswith("Phase4 Test Product")
    assert product["category"]["id"] == product_payload()["category_id"]


def test_create_product_by_normal_user_fails() -> None:
    response = client.post("/admin/products", json=product_payload(), headers=user_headers())

    assert response.status_code == 403


def test_update_product_by_admin_success() -> None:
    product = create_product_as_admin()

    response = client.patch(
        f"/admin/products/{product['id']}",
        json={"price": 23456, "stock": 3},
        headers=admin_headers(),
    )

    assert response.status_code == 200
    assert response.json()["price"] == 23456
    assert response.json()["stock"] == 3


def test_delete_product_by_admin_success() -> None:
    product = create_product_as_admin()

    response = client.delete(f"/admin/products/{product['id']}", headers=admin_headers())

    assert response.status_code == 200
    assert response.json() == {"message": "deleted"}
    assert client.get(f"/products/{product['id']}").status_code == 404
    CREATED_PRODUCT_IDS.remove(product["id"])


def test_search_log_created_when_searching_products() -> None:
    with SessionLocal() as db:
        before = db.scalar(select(func.count(SearchLog.id))) or 0

    response = client.get("/products", params={"keyword": "LiteBook", "limit": 5}, headers=user_headers())

    assert response.status_code == 200
    with SessionLocal() as db:
        after = db.scalar(select(func.count(SearchLog.id))) or 0
        latest = db.scalar(select(SearchLog).order_by(SearchLog.id.desc()))

    assert after == before + 1
    assert latest is not None
    assert latest.keyword == "LiteBook"
    assert latest.user_id is not None
    assert latest.result_count == response.json()["total"]


def test_search_log_anonymous_user_has_null_user_id() -> None:
    with SessionLocal() as db:
        before = db.scalar(select(func.count(SearchLog.id))) or 0

    response = client.get("/products", params={"keyword": "LiteBook", "limit": 5})

    assert response.status_code == 200
    with SessionLocal() as db:
        after = db.scalar(select(func.count(SearchLog.id))) or 0
        latest_log = db.scalar(select(SearchLog).order_by(SearchLog.id.desc()))

    assert after == before + 1
    assert latest_log is not None
    assert latest_log.keyword == "LiteBook"
    assert latest_log.user_id is None
    assert latest_log.result_count == response.json()["total"]


def test_products_with_invalid_token_fails() -> None:
    response = client.get(
        "/products",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_get_categories_success() -> None:
    response = client.get("/categories")

    assert response.status_code == 200
    assert len(response.json()) >= 10


def test_create_category_by_admin_success() -> None:
    slug = f"phase4-{uuid4().hex}"
    response = client.post(
        "/admin/categories",
        json={"name": f"Phase4カテゴリ{uuid4().hex[:8]}", "slug": slug},
        headers=admin_headers(),
    )

    assert response.status_code == 201
    category = response.json()
    CREATED_CATEGORY_IDS.append(category["id"])
    assert category["slug"] == slug
