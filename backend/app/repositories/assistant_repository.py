from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.ai import AIConversation, AIMessage, AIResponseFeedback
from app.models.product import Product


def create_conversation(db: Session, *, user_id: int | None, title: str) -> AIConversation:
    conversation = AIConversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: int) -> AIConversation | None:
    return db.scalar(select(AIConversation).where(AIConversation.id == conversation_id))


def get_conversation_with_messages(db: Session, conversation_id: int) -> AIConversation | None:
    return db.scalar(
        select(AIConversation)
        .options(selectinload(AIConversation.messages))
        .where(AIConversation.id == conversation_id)
    )


def list_conversations_for_user(db: Session, *, user_id: int) -> list[AIConversation]:
    return list(
        db.scalars(
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.updated_at.desc(), AIConversation.id.desc())
        ).all()
    )


def create_message(db: Session, *, conversation_id: int, role: str, content: str) -> AIMessage:
    message = AIMessage(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_message(db: Session, message_id: int) -> AIMessage | None:
    return db.scalar(
        select(AIMessage)
        .options(joinedload(AIMessage.conversation))
        .where(AIMessage.id == message_id)
    )


def touch_conversation(db: Session, conversation: AIConversation) -> None:
    db.execute(
        update(AIConversation)
        .where(AIConversation.id == conversation.id)
        .values(updated_at=func.now())
    )
    db.commit()
    db.refresh(conversation)


def list_candidate_products(db: Session) -> list[Product]:
    return list(
        db.scalars(
            select(Product)
            .options(joinedload(Product.category))
            .order_by(Product.rating.desc().nullslast(), Product.id.asc())
        ).all()
    )


def create_feedback(
    db: Session,
    *,
    message_id: int,
    user_id: int | None,
    rating: str,
    comment: str | None,
) -> AIResponseFeedback:
    feedback = AIResponseFeedback(
        message_id=message_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def list_feedback(db: Session, *, page: int, limit: int) -> tuple[list[AIResponseFeedback], int]:
    total = db.scalar(select(func.count(AIResponseFeedback.id))) or 0
    offset = (page - 1) * limit
    items = list(
        db.scalars(
            select(AIResponseFeedback)
            .options(joinedload(AIResponseFeedback.message).joinedload(AIMessage.conversation))
            .order_by(AIResponseFeedback.created_at.desc(), AIResponseFeedback.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return items, total


def find_previous_user_message(db: Session, *, conversation_id: int, before_message_id: int) -> AIMessage | None:
    return db.scalar(
        select(AIMessage)
        .where(
            AIMessage.conversation_id == conversation_id,
            AIMessage.role == "user",
            AIMessage.id < before_message_id,
        )
        .order_by(AIMessage.id.desc())
    )
