import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.ai import AIConversation, AIResponseFeedback


client = TestClient(app)
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
def cleanup_assistant_records():
    yield
    with SessionLocal() as db:
        if CREATED_FEEDBACK_IDS:
            db.execute(delete(AIResponseFeedback).where(AIResponseFeedback.id.in_(CREATED_FEEDBACK_IDS)))
        if CREATED_CONVERSATION_IDS:
            db.execute(delete(AIConversation).where(AIConversation.id.in_(CREATED_CONVERSATION_IDS)))
        db.commit()
    CREATED_FEEDBACK_IDS.clear()
    CREATED_CONVERSATION_IDS.clear()


def chat(message: str, headers: dict[str, str] | None = None, conversation_id: int | None = None) -> dict:
    payload: dict[str, object] = {"message": message}
    if conversation_id is not None:
        payload["conversation_id"] = conversation_id
    response = client.post("/assistant/chat", json=payload, headers=headers or {})
    assert response.status_code == 200
    body = response.json()
    CREATED_CONVERSATION_IDS.append(body["conversation_id"])
    return body


def test_assistant_chat_returns_recommendations() -> None:
    body = chat("\u0031\u0030\u4e07\u5186\u4ee5\u5185\u3067\u5927\u5b66\u751f\u5411\u3051\u306e\u8efd\u3044\u30ce\u30fc\u30c8PC\u3092\u63a2\u3057\u3066")

    assert body["reply"]
    assert body["recommended_products"]
    assert body["assistant_message_id"]
    assert body["recommended_products"][0]["reason"]


def test_assistant_chat_extracts_price_condition() -> None:
    body = chat("\u0031\u0030\u4e07\u5186\u4ee5\u5185\u3067\u5927\u5b66\u751f\u5411\u3051\u306e\u8efd\u3044\u30ce\u30fc\u30c8PC\u3092\u63a2\u3057\u3066")

    assert body["extracted_conditions"]["max_price"] == 100000


def test_assistant_chat_extracts_category() -> None:
    body = chat("\u5b89\u3044\u30b9\u30de\u30db\u3092\u63a2\u3057\u3066")

    assert body["extracted_conditions"]["category"] == "\u30b9\u30de\u30fc\u30c8\u30d5\u30a9\u30f3"
    assert body["extracted_conditions"]["sort"] == "price_asc"


def test_assistant_chat_saves_conversation() -> None:
    headers = user_headers()
    body = chat("\u0035\u4e07\u5186\u304f\u3089\u3044\u306e\u30a4\u30e4\u30db\u30f3\u3092\u63a2\u3057\u3066", headers=headers)

    response = client.get("/assistant/conversations", headers=headers)
    detail_response = client.get(f"/assistant/conversations/{body['conversation_id']}", headers=headers)

    assert response.status_code == 200
    assert any(item["id"] == body["conversation_id"] for item in response.json()["items"])
    assert detail_response.status_code == 200
    assert len(detail_response.json()["messages"]) == 2


def test_assistant_feedback_good_success() -> None:
    body = chat("\u0031\u0030\u4e07\u5186\u4ee5\u5185\u3067\u5927\u5b66\u751f\u5411\u3051\u306e\u8efd\u3044\u30ce\u30fc\u30c8PC\u3092\u63a2\u3057\u3066", headers=user_headers())

    response = client.post(
        "/assistant/feedback",
        json={"message_id": body["assistant_message_id"], "rating": "good", "comment": "\u6761\u4ef6\u306b\u5408\u3063\u3066\u3044\u305f"},
        headers=user_headers(),
    )

    assert response.status_code == 201
    feedback = response.json()
    CREATED_FEEDBACK_IDS.append(feedback["id"])
    assert feedback["rating"] == "good"
    assert feedback["user_id"] is not None


def test_assistant_feedback_bad_success() -> None:
    body = chat("\u5b89\u3044\u30bf\u30d6\u30ec\u30c3\u30c8\u3092\u63a2\u3057\u3066")

    response = client.post(
        "/assistant/feedback",
        json={"message_id": body["assistant_message_id"], "rating": "bad", "comment": "\u3082\u3063\u3068\u5b89\u3044\u5546\u54c1\u304c\u3088\u3044"},
    )

    assert response.status_code == 201
    feedback = response.json()
    CREATED_FEEDBACK_IDS.append(feedback["id"])
    assert feedback["rating"] == "bad"
    assert feedback["user_id"] is None


def test_assistant_feedback_invalid_rating_fails() -> None:
    body = chat("\u5b89\u3044\u30de\u30a6\u30b9\u3092\u63a2\u3057\u3066")

    response = client.post(
        "/assistant/feedback",
        json={"message_id": body["assistant_message_id"], "rating": "neutral"},
    )

    assert response.status_code == 422


def test_admin_get_ai_evaluations_success() -> None:
    body = chat("\u0031\u0030\u4e07\u5186\u4ee5\u5185\u3067\u5927\u5b66\u751f\u5411\u3051\u306e\u8efd\u3044\u30ce\u30fc\u30c8PC\u3092\u63a2\u3057\u3066", headers=user_headers())
    feedback_response = client.post(
        "/assistant/feedback",
        json={"message_id": body["assistant_message_id"], "rating": "good", "comment": "\u4f7f\u3048\u305d\u3046"},
        headers=user_headers(),
    )
    assert feedback_response.status_code == 201
    CREATED_FEEDBACK_IDS.append(feedback_response.json()["id"])

    response = client.get("/admin/evaluations", headers=admin_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert payload["items"][0]["rating"] in {"good", "bad"}
    assert payload["items"][0]["question"]
    assert payload["items"][0]["assistant_reply"]


def test_normal_user_cannot_get_ai_evaluations() -> None:
    response = client.get("/admin/evaluations", headers=user_headers())

    assert response.status_code == 403
