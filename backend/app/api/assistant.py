from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assistant import (
    AIConversationDetail,
    AIConversationListResponse,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantFeedbackRequest,
    AssistantFeedbackResponse,
)
from app.services.assistant_service import (
    chat_with_assistant,
    get_conversation_detail_for_user,
    get_conversations_for_user,
    save_feedback,
)

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
def chat(
    payload: AssistantChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> AssistantChatResponse:
    return chat_with_assistant(db, payload=payload, current_user=current_user)


@router.get("/conversations", response_model=AIConversationListResponse)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIConversationListResponse:
    return AIConversationListResponse(items=get_conversations_for_user(db, current_user))


@router.get("/conversations/{conversation_id}", response_model=AIConversationDetail)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_conversation_detail_for_user(db, conversation_id, current_user)


@router.post("/feedback", response_model=AssistantFeedbackResponse, status_code=201)
def create_feedback(
    payload: AssistantFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return save_feedback(db, payload=payload, current_user=current_user)
