from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app.db.session import SessionLocal
from app.main import app


client = TestClient(app)

REQUIRED_TABLES = {
    "users",
    "categories",
    "products",
    "favorites",
    "search_logs",
    "click_logs",
    "ai_conversations",
    "ai_messages",
    "ai_response_feedback",
    "daily_search_metrics",
    "product_features",
}


def test_db_connection() -> None:
    with SessionLocal() as db:
        assert db.execute(text("SELECT 1")).scalar_one() == 1

    response = client.get("/debug/db")
    assert response.status_code == 200
    assert response.json() == {"database": "connected"}


def test_required_tables_exist() -> None:
    with SessionLocal() as db:
        inspector = inspect(db.get_bind())
        table_names = set(inspector.get_table_names(schema="public"))

    assert REQUIRED_TABLES.issubset(table_names)
