from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.ai import AIConversation, AIMessage, AIResponseFeedback
from app.models.category import Category
from app.models.log import ClickLog, SearchLog
from app.models.product import Product
from app.models.user import User


client = TestClient(app)

CREATED_PRODUCT_IDS: list[int] = []
CREATED_SEARCH_LOG_IDS: list[int] = []
CREATED_CLICK_LOG_IDS: list[int] = []
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
def cleanup_sql_agent_records():
    yield
    with SessionLocal() as db:
        if CREATED_FEEDBACK_IDS:
            db.execute(delete(AIResponseFeedback).where(AIResponseFeedback.id.in_(CREATED_FEEDBACK_IDS)))
        if CREATED_CONVERSATION_IDS:
            db.execute(delete(AIConversation).where(AIConversation.id.in_(CREATED_CONVERSATION_IDS)))
        if CREATED_CLICK_LOG_IDS:
            db.execute(delete(ClickLog).where(ClickLog.id.in_(CREATED_CLICK_LOG_IDS)))
        if CREATED_SEARCH_LOG_IDS:
            db.execute(delete(SearchLog).where(SearchLog.id.in_(CREATED_SEARCH_LOG_IDS)))
        if CREATED_PRODUCT_IDS:
            db.execute(delete(Product).where(Product.id.in_(CREATED_PRODUCT_IDS)))
        db.commit()

    CREATED_PRODUCT_IDS.clear()
    CREATED_SEARCH_LOG_IDS.clear()
    CREATED_CLICK_LOG_IDS.clear()
    CREATED_CONVERSATION_IDS.clear()
    CREATED_FEEDBACK_IDS.clear()


def seed_sql_agent_records() -> dict[str, object]:
    unique = uuid4().hex
    search_keyword = f"sqlagent-keyword-{unique}"
    no_click_keyword = f"sqlagent-noclick-{unique}"

    with SessionLocal() as db:
        category = db.scalar(select(Category).order_by(Category.id.asc()))
        user = db.scalar(select(User).where(User.email == "user@example.com"))
        assert category is not None
        assert user is not None

        product = Product(
            name=f"SQLAgent Click Product {unique}",
            description=f"This product includes {search_keyword} for sql agent tests.",
            category_id=category.id,
            brand="SQLAgentBrand",
            price=23456,
            rating=4.5,
            stock=5,
            tags=[search_keyword, "sql-agent"],
        )
        db.add(product)
        db.flush()

        search_one = SearchLog(user_id=user.id, keyword=search_keyword, page=1, limit=20, result_count=6)
        search_two = SearchLog(user_id=None, keyword=search_keyword, page=1, limit=20, result_count=4)
        no_click_search = SearchLog(user_id=None, keyword=no_click_keyword, page=1, limit=20, result_count=3)
        category_search_one = SearchLog(user_id=user.id, category_id=category.id, page=1, limit=20, result_count=9)
        category_search_two = SearchLog(user_id=None, category_id=category.id, page=1, limit=20, result_count=11)
        click_one = ClickLog(user_id=user.id, product_id=product.id, source="search")
        click_two = ClickLog(user_id=None, product_id=product.id, source="assistant")
        conversation = AIConversation(user_id=user.id, title="sql agent conversation")
        db.add_all([
            search_one,
            search_two,
            no_click_search,
            category_search_one,
            category_search_two,
            click_one,
            click_two,
            conversation,
        ])
        db.flush()

        user_message = AIMessage(conversation_id=conversation.id, role="user", content="Which product should I choose?")
        assistant_message = AIMessage(conversation_id=conversation.id, role="assistant", content="You should choose this product.")
        db.add_all([user_message, assistant_message])
        db.flush()

        bad_feedback = AIResponseFeedback(
            message_id=assistant_message.id,
            user_id=user.id,
            rating="bad",
            comment="Needs a clearer reason",
        )
        db.add(bad_feedback)
        db.flush()

        ids = {
            "search_keyword": search_keyword,
            "no_click_keyword": no_click_keyword,
            "product_id": product.id,
            "product_name": product.name,
            "category_name": category.name,
            "assistant_message_id": assistant_message.id,
        }
        CREATED_PRODUCT_IDS.append(product.id)
        CREATED_SEARCH_LOG_IDS.extend([
            search_one.id,
            search_two.id,
            no_click_search.id,
            category_search_one.id,
            category_search_two.id,
        ])
        CREATED_CLICK_LOG_IDS.extend([click_one.id, click_two.id])
        CREATED_CONVERSATION_IDS.append(conversation.id)
        CREATED_FEEDBACK_IDS.append(bad_feedback.id)
        db.commit()
        return ids


def query(question: str, headers: dict[str, str] | None = None):
    return client.post(
        "/admin/sql-agent/query",
        json={"question": question},
        headers=headers or admin_headers(),
    )


def test_sql_agent_top_search_keywords() -> None:
    seeded = seed_sql_agent_records()

    response = query("よく検索されているキーワードを教えて")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "top_search_keywords"
    assert body["columns"] == ["keyword", "search_count"]
    rows = {row[0]: row[1] for row in body["rows"]}
    assert rows[seeded["search_keyword"]] == 2


def test_sql_agent_top_clicked_products() -> None:
    seeded = seed_sql_agent_records()

    response = query("よくクリックされている商品は？")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "top_clicked_products"
    assert body["columns"] == ["product_id", "product_name", "click_count"]
    row = next(row for row in body["rows"] if row[0] == seeded["product_id"])
    assert row[1] == seeded["product_name"]
    assert row[2] == 2


def test_sql_agent_no_click_keywords() -> None:
    seeded = seed_sql_agent_records()

    response = query("検索されたがクリックされなかったキーワードを教えて")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "no_click_keywords"
    assert body["columns"] == ["keyword", "search_count", "click_count"]
    row = next(row for row in body["rows"] if row[0] == seeded["no_click_keyword"])
    assert row[1] == 1
    assert row[2] == 0


def test_sql_agent_category_search_counts() -> None:
    seeded = seed_sql_agent_records()

    response = query("カテゴリ別の検索回数を教えて")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "category_search_counts"
    assert body["columns"] == ["category_name", "search_count"]
    rows = {row[0]: row[1] for row in body["rows"]}
    assert rows[seeded["category_name"]] >= 2


def test_sql_agent_assistant_bad_feedback() -> None:
    seeded = seed_sql_agent_records()

    response = query("AI回答で不満が多いものを見たい")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "assistant_bad_feedback"
    assert body["columns"] == ["message_id", "question", "answer", "comment", "created_at"]
    row = next(row for row in body["rows"] if row[0] == seeded["assistant_message_id"])
    assert row[1] == "Which product should I choose?"
    assert row[2] == "You should choose this product."
    assert row[3] == "Needs a clearer reason"
    assert row[4]


def test_sql_agent_unknown_question_returns_suggestions() -> None:
    response = query("売上と在庫の関係をSQLで調べて")

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "unknown"
    assert body["rows"] == []
    assert body["columns"] == []
    assert body["suggestions"]


def test_sql_agent_requires_admin() -> None:
    response = client.post("/admin/sql-agent/query", json={"question": "今月，最も検索されたキーワードは？"})

    assert response.status_code == 401


def test_sql_agent_rejects_normal_user() -> None:
    response = query(
        "今月，最も検索されたキーワードは？",
        headers=user_headers(),
    )

    assert response.status_code == 403
