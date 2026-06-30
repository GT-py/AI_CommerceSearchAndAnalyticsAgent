from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.ai import AIConversation, AIMessage, AIResponseFeedback
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
CREATED_CONVERSATION_IDS: list[int] = []
CREATED_FEEDBACK_IDS: list[int] = []


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('admin@example.com', 'adminpass')}"}


def user_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('user@example.com', 'userpass')}"}


@pytest.fixture(autouse=True)
def cleanup_analytics_records():
    yield
    with SessionLocal() as db:
        if CREATED_FEEDBACK_IDS:
            db.execute(delete(AIResponseFeedback).where(AIResponseFeedback.id.in_(CREATED_FEEDBACK_IDS)))
        if CREATED_CONVERSATION_IDS:
            db.execute(delete(AIConversation).where(AIConversation.id.in_(CREATED_CONVERSATION_IDS)))
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
    CREATED_CONVERSATION_IDS.clear()
    CREATED_FEEDBACK_IDS.clear()


def seed_analytics_records() -> dict[str, object]:
    keyword = f"analytics-{uuid4().hex}"
    with SessionLocal() as db:
        category = db.scalar(select(Category).order_by(Category.id.asc()))
        user = db.scalar(select(User).where(User.email == "user@example.com"))
        assert category is not None
        assert user is not None

        product = Product(
            name=f"Analytics Test Product {uuid4().hex}",
            description="Product used by analytics tests.",
            category_id=category.id,
            brand="AnalyticsBrand",
            price=12345,
            rating=4.6,
            stock=8,
            tags=["analytics", "test"],
        )
        db.add(product)
        db.flush()

        search_one = SearchLog(
            user_id=user.id,
            keyword=keyword,
            page=1,
            limit=20,
            result_count=7,
        )
        search_two = SearchLog(
            user_id=None,
            keyword=keyword,
            page=1,
            limit=20,
            result_count=13,
        )
        click_search = ClickLog(user_id=None, product_id=product.id, source="search")
        click_assistant = ClickLog(user_id=user.id, product_id=product.id, source="assistant")
        favorite = Favorite(user_id=user.id, product_id=product.id)
        conversation = AIConversation(user_id=user.id, title="analytics conversation")
        db.add_all([search_one, search_two, click_search, click_assistant, favorite, conversation])
        db.flush()

        user_message = AIMessage(conversation_id=conversation.id, role="user", content="Need a product")
        assistant_good = AIMessage(conversation_id=conversation.id, role="assistant", content="Good answer")
        assistant_bad = AIMessage(conversation_id=conversation.id, role="assistant", content="Bad answer")
        db.add_all([user_message, assistant_good, assistant_bad])
        db.flush()

        good_feedback = AIResponseFeedback(
            message_id=assistant_good.id,
            user_id=user.id,
            rating="good",
            comment="Useful",
        )
        bad_feedback = AIResponseFeedback(
            message_id=assistant_bad.id,
            user_id=user.id,
            rating="bad",
            comment="Not enough detail",
        )
        db.add_all([good_feedback, bad_feedback])
        db.flush()

        ids = {
            "product_id": product.id,
            "keyword": keyword,
            "bad_message_id": assistant_bad.id,
        }
        CREATED_PRODUCT_IDS.append(product.id)
        CREATED_SEARCH_LOG_IDS.extend([search_one.id, search_two.id])
        CREATED_CLICK_LOG_IDS.extend([click_search.id, click_assistant.id])
        CREATED_FAVORITE_IDS.append(favorite.id)
        CREATED_CONVERSATION_IDS.append(conversation.id)
        CREATED_FEEDBACK_IDS.extend([good_feedback.id, bad_feedback.id])
        db.commit()
        return ids


def test_admin_analytics_summary_success() -> None:
    seed_analytics_records()

    response = client.get("/admin/analytics/summary", headers=admin_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["total_products"] >= 1
    assert body["total_users"] >= 2
    assert body["total_searches"] >= 2
    assert body["total_clicks"] >= 2
    assert body["total_ai_conversations"] >= 1
    assert body["total_ai_feedback"] >= 2
    assert body["good_feedback_count"] >= 1
    assert body["bad_feedback_count"] >= 1


def test_admin_analytics_search_keywords_success() -> None:
    seeded = seed_analytics_records()

    response = client.get("/admin/analytics/search-keywords", params={"limit": 100}, headers=admin_headers())

    assert response.status_code == 200
    items = response.json()["items"]
    item = next(item for item in items if item["keyword"] == seeded["keyword"])
    assert item["search_count"] == 2
    assert item["total_result_count"] == 20
    assert item["avg_result_count"] == 10.0


def test_admin_analytics_products_success() -> None:
    seeded = seed_analytics_records()

    response = client.get("/admin/analytics/products", params={"limit": 100}, headers=admin_headers())

    assert response.status_code == 200
    items = response.json()["items"]
    item = next(item for item in items if item["product_id"] == seeded["product_id"])
    assert item["click_count"] == 2
    assert item["favorite_count"] == 1
    assert item["assistant_recommendation_clicks"] == 1
    assert item["name"].startswith("Analytics Test Product")
    assert item["category"]


def test_admin_analytics_assistant_feedback_success() -> None:
    seeded = seed_analytics_records()

    response = client.get(
        "/admin/analytics/assistant-feedback",
        params={"recent_limit": 20},
        headers=admin_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["good"] >= 1
    assert body["bad"] >= 1
    assert 0 <= body["good_rate"] <= 1
    assert any(item["message_id"] == seeded["bad_message_id"] for item in body["recent_bad_feedback"])


def test_normal_user_cannot_access_analytics() -> None:
    headers = user_headers()
    paths = [
        "/admin/analytics/summary",
        "/admin/analytics/search-keywords",
        "/admin/analytics/products",
        "/admin/analytics/assistant-feedback",
    ]

    for path in paths:
        response = client.get(path, headers=headers)
        assert response.status_code == 403


def test_unauthenticated_user_cannot_access_analytics() -> None:
    paths = [
        "/admin/analytics/summary",
        "/admin/analytics/search-keywords",
        "/admin/analytics/products",
        "/admin/analytics/assistant-feedback",
    ]

    for path in paths:
        response = client.get(path)
        assert response.status_code == 401
