from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.analytics import DailySearchMetric, ProductFeature
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.log import ClickLog, SearchLog
from app.models.product import Product
from app.models.user import User


client = TestClient(app)

CREATED_PRODUCT_IDS: list[int] = []
CREATED_SEARCH_LOG_IDS: list[int] = []
CREATED_CLICK_LOG_IDS: list[int] = []
CREATED_FAVORITE_IDS: list[int] = []
CREATED_KEYWORDS: list[str] = []


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('admin@example.com', 'adminpass')}"}


def user_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('user@example.com', 'userpass')}"}


@pytest.fixture(autouse=True)
def cleanup_etl_records():
    yield
    with SessionLocal() as db:
        if CREATED_PRODUCT_IDS:
            db.execute(delete(ProductFeature).where(ProductFeature.product_id.in_(CREATED_PRODUCT_IDS)))
        if CREATED_KEYWORDS:
            db.execute(delete(DailySearchMetric).where(DailySearchMetric.keyword.in_(CREATED_KEYWORDS)))
        if CREATED_CLICK_LOG_IDS:
            db.execute(delete(ClickLog).where(ClickLog.id.in_(CREATED_CLICK_LOG_IDS)))
        if CREATED_FAVORITE_IDS:
            db.execute(delete(Favorite).where(Favorite.id.in_(CREATED_FAVORITE_IDS)))
        if CREATED_SEARCH_LOG_IDS:
            db.execute(delete(SearchLog).where(SearchLog.id.in_(CREATED_SEARCH_LOG_IDS)))
        if CREATED_PRODUCT_IDS:
            db.execute(delete(Product).where(Product.id.in_(CREATED_PRODUCT_IDS)))
        db.commit()

    CREATED_PRODUCT_IDS.clear()
    CREATED_SEARCH_LOG_IDS.clear()
    CREATED_CLICK_LOG_IDS.clear()
    CREATED_FAVORITE_IDS.clear()
    CREATED_KEYWORDS.clear()


def seed_etl_records() -> dict[str, object]:
    keyword = f"etl-keyword-{uuid4().hex}"
    with SessionLocal() as db:
        category = db.scalar(select(Category).order_by(Category.id.asc()))
        user = db.scalar(select(User).where(User.email == "user@example.com"))
        assert category is not None
        assert user is not None

        product = Product(
            name=f"ETL Test Product {uuid4().hex}",
            description="Product used by ETL tests.",
            category_id=category.id,
            brand="ETLBrand",
            price=34567,
            rating=4.2,
            stock=7,
            tags=["etl", "test"],
        )
        db.add(product)
        db.flush()

        search_one = SearchLog(user_id=user.id, keyword=keyword, page=1, limit=20, result_count=3)
        search_two = SearchLog(user_id=None, keyword=keyword, page=1, limit=20, result_count=5)
        click_one = ClickLog(user_id=user.id, product_id=product.id, source="search")
        click_two = ClickLog(user_id=None, product_id=product.id, source="assistant")
        favorite = Favorite(user_id=user.id, product_id=product.id)
        db.add_all([search_one, search_two, click_one, click_two, favorite])
        db.flush()

        data = {
            "keyword": keyword,
            "product_id": product.id,
            "product_name": product.name,
        }
        CREATED_PRODUCT_IDS.append(product.id)
        CREATED_KEYWORDS.append(keyword)
        CREATED_SEARCH_LOG_IDS.extend([search_one.id, search_two.id])
        CREATED_CLICK_LOG_IDS.extend([click_one.id, click_two.id])
        CREATED_FAVORITE_IDS.append(favorite.id)
        db.commit()
        return data


def run_etl() -> dict:
    response = client.post("/admin/etl/run", headers=admin_headers())
    assert response.status_code == 200
    return response.json()


def test_admin_run_etl_success() -> None:
    seed_etl_records()

    body = run_etl()

    assert body["message"] == "ETL completed"
    assert body["daily_search_metrics_count"] >= 1
    assert body["product_features_count"] >= 1


def test_normal_user_cannot_run_etl() -> None:
    response = client.post("/admin/etl/run", headers=user_headers())

    assert response.status_code == 403


def test_daily_search_metrics_created() -> None:
    seeded = seed_etl_records()
    run_etl()

    with SessionLocal() as db:
        metric = db.scalar(select(DailySearchMetric).where(DailySearchMetric.keyword == seeded["keyword"]))

    assert metric is not None
    assert metric.search_count == 2
    assert metric.click_count >= 2
    assert metric.ctr >= 1


def test_product_features_created() -> None:
    seeded = seed_etl_records()
    run_etl()

    with SessionLocal() as db:
        feature = db.scalar(
            select(ProductFeature).where(
                ProductFeature.product_id == seeded["product_id"],
                ProductFeature.date == date.today(),
            )
        )

    assert feature is not None
    assert feature.view_count_7d == 2
    assert feature.click_count_7d == 2
    assert feature.favorite_count_7d == 1
    assert feature.ctr_7d == 1


def test_get_daily_search_metrics_success() -> None:
    seeded = seed_etl_records()
    run_etl()

    response = client.get(
        "/admin/metrics/daily-search",
        params={"keyword": seeded["keyword"], "limit": 20},
        headers=admin_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"]
    assert body["items"][0]["keyword"] == seeded["keyword"]
    assert body["items"][0]["search_count"] == 2


def test_get_product_features_success() -> None:
    seeded = seed_etl_records()
    run_etl()

    response = client.get(
        "/admin/features/products",
        params={"date": date.today().isoformat(), "limit": 100},
        headers=admin_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    item = next(item for item in body["items"] if item["product_id"] == seeded["product_id"])
    assert item["product_name"] == seeded["product_name"]
    assert item["click_count_7d"] == 2
    assert item["favorite_count_7d"] == 1
