import re
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ai import AIConversation, AIMessage, AIResponseFeedback
from app.models.product import Product
from app.models.user import User
from app.repositories.assistant_repository import (
    create_conversation,
    create_feedback,
    create_message,
    find_previous_user_message,
    get_conversation,
    get_conversation_with_messages,
    get_message,
    list_candidate_products,
    list_conversations_for_user,
    list_feedback,
    touch_conversation,
)
from app.schemas.assistant import (
    AIEvaluationListResponse,
    AIEvaluationRead,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantFeedbackRequest,
    AssistantFeedbackResponse,
    ExtractedConditions,
    RecommendedProduct,
)

CATEGORY_KEYWORDS: list[tuple[str, str]] = [
    ("\u30ce\u30fc\u30c8PC", "\u30ce\u30fc\u30c8PC"),
    ("\u30d1\u30bd\u30b3\u30f3", "\u30ce\u30fc\u30c8PC"),
    ("PC", "\u30ce\u30fc\u30c8PC"),
    ("\u30b9\u30de\u30fc\u30c8\u30d5\u30a9\u30f3", "\u30b9\u30de\u30fc\u30c8\u30d5\u30a9\u30f3"),
    ("\u30b9\u30de\u30db", "\u30b9\u30de\u30fc\u30c8\u30d5\u30a9\u30f3"),
    ("\u30bf\u30d6\u30ec\u30c3\u30c8", "\u30bf\u30d6\u30ec\u30c3\u30c8"),
    ("\u30ef\u30a4\u30e4\u30ec\u30b9\u30a4\u30e4\u30db\u30f3", "\u30a4\u30e4\u30db\u30f3"),
    ("\u30a4\u30e4\u30db\u30f3", "\u30a4\u30e4\u30db\u30f3"),
    ("\u30c7\u30a3\u30b9\u30d7\u30ec\u30a4", "\u30e2\u30cb\u30bf\u30fc"),
    ("\u30e2\u30cb\u30bf\u30fc", "\u30e2\u30cb\u30bf\u30fc"),
    ("\u30ad\u30fc\u30dc\u30fc\u30c9", "\u30ad\u30fc\u30dc\u30fc\u30c9"),
    ("\u30de\u30a6\u30b9", "\u30de\u30a6\u30b9"),
    ("\u30c1\u30a7\u30a2", "\u30c7\u30b9\u30af\u30c1\u30a7\u30a2"),
    ("\u6905\u5b50", "\u30c7\u30b9\u30af\u30c1\u30a7\u30a2"),
    ("\u66f8\u7c4d", "\u66f8\u7c4d"),
    ("\u672c", "\u66f8\u7c4d"),
    ("\u5bb6\u96fb", "\u751f\u6d3b\u5bb6\u96fb"),
]

TAG_KEYWORDS = [
    "\u5927\u5b66\u751f\u5411\u3051",
    "\u8efd\u91cf",
    "\u9577\u6642\u9593\u30d0\u30c3\u30c6\u30ea\u30fc",
    "\u5728\u5b85\u52e4\u52d9",
    "\u30aa\u30f3\u30e9\u30a4\u30f3\u6388\u696d",
    "\u901a\u5b66",
    "\u30ec\u30dd\u30fc\u30c8\u4f5c\u6210",
    "\u30b2\u30fc\u30e0",
    "\u9ad8\u6027\u80fd",
    "\u30b3\u30b9\u30d1",
    "\u521d\u5fc3\u8005\u5411\u3051",
]


@dataclass
class ScoredProduct:
    product: Product
    score: int
    reason: str


def extract_conditions(message: str) -> ExtractedConditions:
    normalized = message.upper()
    conditions = ExtractedConditions()

    man_yen_matches = re.findall(r"(\d+)\s*\u4e07\s*\u5186?", message)
    yen_matches = re.findall(r"(\d{4,})\s*\u5186", message)
    if man_yen_matches:
        conditions.max_price = int(man_yen_matches[0]) * 10000
    elif yen_matches:
        conditions.max_price = int(yen_matches[0])

    if "\u5b89\u3044" in message or "\u9ad8\u3059\u304e\u306a\u3044" in message:
        conditions.sort = "price_asc"

    for keyword, category in CATEGORY_KEYWORDS:
        if keyword.upper() in normalized:
            conditions.category = category
            break

    tags: list[str] = []
    for tag in TAG_KEYWORDS:
        if tag in message and tag not in tags:
            tags.append(tag)
    if "\u8efd\u3044" in message and "\u8efd\u91cf" not in tags:
        tags.append("\u8efd\u91cf")
    if "\u9577\u6642\u9593" in message and "\u9577\u6642\u9593\u30d0\u30c3\u30c6\u30ea\u30fc" not in tags:
        tags.append("\u9577\u6642\u9593\u30d0\u30c3\u30c6\u30ea\u30fc")
    conditions.tags = tags

    if "\u8efd\u3044" in message or "\u8efd\u91cf" in message:
        conditions.max_weight_g = 1200
    if "\u9577\u6642\u9593" in message or "\u30d0\u30c3\u30c6\u30ea\u30fc" in message:
        conditions.min_battery_hours = 10

    memory_match = re.search(r"\u30e1\u30e2\u30ea\s*(\d+)\s*GB", message, flags=re.IGNORECASE)
    if memory_match:
        conditions.min_memory_gb = int(memory_match.group(1))

    storage_match = re.search(r"(\d+)\s*GB", message, flags=re.IGNORECASE)
    if storage_match:
        value = int(storage_match.group(1))
        if conditions.min_memory_gb is None or value != conditions.min_memory_gb:
            conditions.min_storage_gb = value

    return conditions


def create_title(message: str) -> str:
    title = message.strip().replace("\n", " ")
    return title[:40] if len(title) > 40 else title


def product_text(product: Product) -> str:
    values = [product.name, product.description, product.brand or "", product.category.name, *product.tags]
    return " ".join(values)


def score_product(product: Product, conditions: ExtractedConditions) -> ScoredProduct | None:
    score = 0
    reasons: list[str] = []
    text = product_text(product)

    if conditions.category:
        if product.category.name == conditions.category:
            score += 3
            reasons.append(f"\u30ab\u30c6\u30b4\u30ea\u304c{conditions.category}\u306b\u4e00\u81f4\u3057\u3066\u3044\u307e\u3059")
        else:
            return None

    if conditions.max_price is not None:
        if product.price <= conditions.max_price:
            score += 2
            reasons.append(f"\u4fa1\u683c\u304c{conditions.max_price:,}\u5186\u4ee5\u5185\u3067\u3059")
        else:
            return None

    for tag in conditions.tags:
        if tag in product.tags or tag in text:
            score += 1
            reasons.append(f"{tag}\u306b\u5408\u3046\u8981\u7d20\u304c\u3042\u308a\u307e\u3059")

    if conditions.max_weight_g is not None and product.weight_g is not None:
        if product.weight_g <= conditions.max_weight_g:
            score += 1
            reasons.append("\u8efd\u91cf\u3067\u6301\u3061\u904b\u3073\u3057\u3084\u3059\u3044\u3067\u3059")
    if conditions.min_battery_hours is not None and product.battery_hours is not None:
        if product.battery_hours >= conditions.min_battery_hours:
            score += 1
            reasons.append("\u30d0\u30c3\u30c6\u30ea\u30fc\u6642\u9593\u304c\u9577\u3081\u3067\u3059")
    if conditions.min_memory_gb is not None and product.memory_gb is not None:
        if product.memory_gb >= conditions.min_memory_gb:
            score += 1
            reasons.append(f"\u30e1\u30e2\u30ea\u304c{conditions.min_memory_gb}GB\u4ee5\u4e0a\u3067\u3059")
        else:
            return None
    if conditions.min_storage_gb is not None and product.storage_gb is not None:
        if product.storage_gb >= conditions.min_storage_gb:
            score += 1
            reasons.append(f"\u30b9\u30c8\u30ec\u30fc\u30b8\u304c{conditions.min_storage_gb}GB\u4ee5\u4e0a\u3067\u3059")

    if product.rating is not None and product.rating >= 4.3:
        score += 1
        reasons.append("\u8a55\u4fa1\u304c\u9ad8\u3081\u3067\u3059")

    if score == 0:
        return None

    reason = "\u3053\u306e\u5546\u54c1\u306f" + "\u3001".join(reasons[:4]) + "\u3002"
    return ScoredProduct(product=product, score=score, reason=reason)


def recommend_products(products: list[Product], conditions: ExtractedConditions) -> list[RecommendedProduct]:
    scored = [item for product in products if (item := score_product(product, conditions)) is not None]
    if conditions.sort == "price_asc":
        scored.sort(key=lambda item: (item.product.price, -item.score, item.product.id))
    else:
        scored.sort(key=lambda item: (-item.score, item.product.price, item.product.id))

    return [
        RecommendedProduct(
            id=item.product.id,
            name=item.product.name,
            price=item.product.price,
            reason=item.reason,
        )
        for item in scored[:5]
    ]


def build_reply(conditions: ExtractedConditions, recommendations: list[RecommendedProduct]) -> str:
    if not recommendations:
        return "\u6761\u4ef6\u306b\u5b8c\u5168\u306b\u5408\u3046\u5546\u54c1\u306f\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3067\u3057\u305f\u3002\u6761\u4ef6\u3092\u5c11\u3057\u5e83\u3052\u3066\u691c\u7d22\u3057\u3066\u307f\u3066\u304f\u3060\u3055\u3044\u3002"

    pieces: list[str] = []
    if conditions.max_price is not None:
        pieces.append(f"{conditions.max_price:,}\u5186\u4ee5\u5185")
    if conditions.category:
        pieces.append(conditions.category)
    pieces.extend(conditions.tags[:3])
    condition_text = "\u30fb".join(pieces) if pieces else "\u3054\u5e0c\u671b"
    return f"{condition_text}\u306e\u6761\u4ef6\u306b\u5408\u3046\u5546\u54c1\u3092{len(recommendations)}\u4ef6\u898b\u3064\u3051\u307e\u3057\u305f\u3002\u7528\u9014\u3068\u4fa1\u683c\u306e\u30d0\u30e9\u30f3\u30b9\u3092\u898b\u3066\u9078\u3093\u3067\u3044\u307e\u3059\u3002"


def ensure_conversation(
    db: Session,
    *,
    conversation_id: int | None,
    current_user: User | None,
    message: str,
) -> AIConversation:
    if conversation_id is None:
        return create_conversation(
            db,
            user_id=current_user.id if current_user else None,
            title=create_title(message),
        )

    conversation = get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if current_user is not None and conversation.user_id not in (None, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation access denied")
    if current_user is None and conversation.user_id is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return conversation


def chat_with_assistant(
    db: Session,
    *,
    payload: AssistantChatRequest,
    current_user: User | None,
) -> AssistantChatResponse:
    conversation = ensure_conversation(
        db,
        conversation_id=payload.conversation_id,
        current_user=current_user,
        message=payload.message,
    )
    create_message(db, conversation_id=conversation.id, role="user", content=payload.message)

    conditions = extract_conditions(payload.message)
    recommendations = recommend_products(list_candidate_products(db), conditions)
    reply = build_reply(conditions, recommendations)
    assistant_message = create_message(db, conversation_id=conversation.id, role="assistant", content=reply)
    touch_conversation(db, conversation)

    return AssistantChatResponse(
        conversation_id=conversation.id,
        assistant_message_id=assistant_message.id,
        reply=reply,
        extracted_conditions=conditions,
        recommended_products=recommendations,
    )


def get_conversations_for_user(db: Session, current_user: User) -> list[AIConversation]:
    return list_conversations_for_user(db, user_id=current_user.id)


def get_conversation_detail_for_user(db: Session, conversation_id: int, current_user: User) -> AIConversation:
    conversation = get_conversation_with_messages(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conversation access denied")
    conversation.messages.sort(key=lambda message: message.id)
    return conversation


def save_feedback(
    db: Session,
    *,
    payload: AssistantFeedbackRequest,
    current_user: User | None,
) -> AIResponseFeedback:
    message = get_message(db, payload.message_id)
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if message.role != "assistant":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback target must be assistant message")

    return create_feedback(
        db,
        message_id=payload.message_id,
        user_id=current_user.id if current_user else None,
        rating=payload.rating,
        comment=payload.comment,
    )


def get_admin_ai_evaluations(db: Session, *, page: int, limit: int) -> AIEvaluationListResponse:
    items, total = list_feedback(db, page=page, limit=limit)
    evaluations: list[AIEvaluationRead] = []
    for feedback in items:
        message = feedback.message
        question = find_previous_user_message(
            db,
            conversation_id=message.conversation_id,
            before_message_id=message.id,
        )
        evaluations.append(
            AIEvaluationRead(
                id=feedback.id,
                created_at=feedback.created_at,
                user_id=feedback.user_id,
                question=question.content if question else None,
                assistant_reply=message.content,
                rating=feedback.rating,
                comment=feedback.comment,
            )
        )

    return AIEvaluationListResponse(
        items=evaluations,
        page=page,
        limit=limit,
        total=total,
        has_next=page * limit < total,
    )
