import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models.favorite import Favorite
from app.models.log import ClickLog
from app.models.user import User


client = TestClient(app)
CREATED_CLICK_LOG_IDS: list[int] = []


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('admin@example.com', 'adminpass')}"}


def user_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {login('user@example.com', 'userpass')}"}


def first_product() -> dict:
    response = client.get("/products", params={"limit": 1})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    return items[0]


def user_id_by_email(email: str) -> int | None:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        return user.id if user else None


@pytest.fixture(autouse=True)
def cleanup_records():
    user_id = user_id_by_email("user@example.com")
    with SessionLocal() as db:
        if user_id is not None:
            db.execute(delete(Favorite).where(Favorite.user_id == user_id))
        db.commit()

    yield

    with SessionLocal() as db:
        if CREATED_CLICK_LOG_IDS:
            db.execute(delete(ClickLog).where(ClickLog.id.in_(CREATED_CLICK_LOG_IDS)))
        if user_id is not None:
            db.execute(delete(Favorite).where(Favorite.user_id == user_id))
        db.commit()
    CREATED_CLICK_LOG_IDS.clear()


def test_add_favorite_success() -> None:
    product = first_product()

    response = client.post(f"/favorites/{product['id']}", headers=user_headers())

    assert response.status_code == 201
    body = response.json()
    assert body["product"]["id"] == product["id"]
    assert body["product"]["name"] == product["name"]


def test_add_favorite_duplicate_is_safe() -> None:
    product = first_product()
    headers = user_headers()

    first = client.post(f"/favorites/{product['id']}", headers=headers)
    second = client.post(f"/favorites/{product['id']}", headers=headers)

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["product"]["id"] == product["id"]
    with SessionLocal() as db:
        user_id = user_id_by_email("user@example.com")
        count = len(
            list(
                db.scalars(
                    select(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product["id"])
                )
            )
        )
    assert count == 1


def test_remove_favorite_success() -> None:
    product = first_product()
    headers = user_headers()
    assert client.post(f"/favorites/{product['id']}", headers=headers).status_code == 201

    response = client.delete(f"/favorites/{product['id']}", headers=headers)
    second_response = client.delete(f"/favorites/{product['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "removed"}
    assert second_response.status_code == 200


def test_get_favorites_success() -> None:
    product = first_product()
    headers = user_headers()
    assert client.post(f"/favorites/{product['id']}", headers=headers).status_code == 201

    response = client.get("/favorites", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["product"]["id"] == product["id"]


def test_favorite_requires_login() -> None:
    product = first_product()

    get_response = client.get("/favorites")
    post_response = client.post(f"/favorites/{product['id']}")
    delete_response = client.delete(f"/favorites/{product['id']}")

    assert get_response.status_code == 401
    assert post_response.status_code == 401
    assert delete_response.status_code == 401


def test_create_click_log_without_login_success() -> None:
    product = first_product()

    response = client.post("/logs/click", json={"product_id": product["id"], "source": "search"})

    assert response.status_code == 201
    body = response.json()
    CREATED_CLICK_LOG_IDS.append(body["id"])
    assert body["product_id"] == product["id"]
    assert body["source"] == "search"
    assert body["user_id"] is None


def test_create_click_log_with_login_success() -> None:
    product = first_product()

    response = client.post(
        "/logs/click",
        json={"product_id": product["id"], "source": "favorite"},
        headers=user_headers(),
    )

    assert response.status_code == 201
    body = response.json()
    CREATED_CLICK_LOG_IDS.append(body["id"])
    assert body["product_id"] == product["id"]
    assert body["source"] == "favorite"
    assert body["user_id"] is not None


def test_admin_get_search_logs_success() -> None:
    response = client.get("/products", params={"keyword": "LiteBook", "limit": 3})
    assert response.status_code == 200

    logs_response = client.get("/admin/logs/search", headers=admin_headers())

    assert logs_response.status_code == 200
    body = logs_response.json()
    assert body["items"]
    assert body["page"] == 1
    assert body["limit"] == 20
    assert {"user_id", "keyword", "result_count", "created_at"}.issubset(body["items"][0].keys())


def test_admin_get_click_logs_success() -> None:
    product = first_product()
    click_response = client.post("/logs/click", json={"product_id": product["id"], "source": "search"})
    assert click_response.status_code == 201
    CREATED_CLICK_LOG_IDS.append(click_response.json()["id"])

    logs_response = client.get("/admin/logs/clicks", headers=admin_headers())

    assert logs_response.status_code == 200
    body = logs_response.json()
    assert body["items"]
    assert body["items"][0]["product"]["name"]
    assert {"user_id", "product_id", "source", "created_at"}.issubset(body["items"][0].keys())


def test_normal_user_cannot_get_admin_logs() -> None:
    headers = user_headers()

    search_response = client.get("/admin/logs/search", headers=headers)
    click_response = client.get("/admin/logs/clicks", headers=headers)

    assert search_response.status_code == 403
    assert click_response.status_code == 403
