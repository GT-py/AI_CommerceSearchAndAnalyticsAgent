from uuid import uuid4

import pytest
from sqlalchemy import delete
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_admin_user
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


client = TestClient(app)

CREATED_EMAILS: list[str] = []


@pytest.fixture(autouse=True)
def cleanup_created_users():
    yield
    if not CREATED_EMAILS:
        return
    with SessionLocal() as db:
        db.execute(delete(User).where(User.email.in_(CREATED_EMAILS)))
        db.commit()
    CREATED_EMAILS.clear()


def unique_email(prefix: str = "phase3") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def register_user(email: str, password: str = "password123") -> dict:
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201
    CREATED_EMAILS.append(email)
    return response.json()


def login_user(email: str, password: str = "password123") -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    return body["access_token"]


def test_register_success() -> None:
    email = unique_email("register-success")

    body = register_user(email)

    assert body["email"] == email
    assert body["role"] == "user"
    assert "id" in body
    assert "hashed_password" not in body


def test_register_invalid_email_fails() -> None:
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )

    assert response.status_code == 422


def test_register_duplicate_email_fails() -> None:
    email = unique_email("register-duplicate")
    register_user(email)

    response = client.post("/auth/register", json={"email": email, "password": "password123"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_login_invalid_email_fails() -> None:
    response = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "password123"},
    )

    assert response.status_code == 422


def test_login_success() -> None:
    email = unique_email("login-success")
    register_user(email)

    token = login_user(email)

    assert isinstance(token, str)


def test_login_wrong_password_fails() -> None:
    email = unique_email("login-wrong")
    register_user(email)

    response = client.post("/auth/login", json={"email": email, "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_get_me_success() -> None:
    email = unique_email("me-success")
    registered = register_user(email)
    token = login_user(email)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "id": registered["id"],
        "email": email,
        "role": "user",
    }


def test_get_me_without_token_fails() -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_with_invalid_token_fails() -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_admin_dependency_allows_admin() -> None:
    admin = User(id=1, email="admin@example.com", hashed_password="hash", role="admin")

    assert get_current_admin_user(admin) is admin


def test_admin_dependency_rejects_normal_user() -> None:
    normal_user = User(id=2, email="user@example.com", hashed_password="hash", role="user")

    with pytest.raises(HTTPException) as exc_info:
        get_current_admin_user(normal_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Admin privileges required"
