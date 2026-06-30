from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExtractedConditions(BaseModel):
    category: str | None = None
    max_price: int | None = None
    sort: str | None = None
    tags: list[str] = Field(default_factory=list)
    min_battery_hours: int | None = None
    max_weight_g: int | None = None
    min_memory_gb: int | None = None
    min_storage_gb: int | None = None


class AssistantChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(min_length=1, max_length=2000)


class RecommendedProduct(BaseModel):
    id: int
    name: str
    price: int
    reason: str


class AssistantChatResponse(BaseModel):
    conversation_id: int
    assistant_message_id: int
    reply: str
    extracted_conditions: ExtractedConditions
    recommended_products: list[RecommendedProduct]


class AIMessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIConversationRead(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIConversationDetail(AIConversationRead):
    messages: list[AIMessageRead]


class AIConversationListResponse(BaseModel):
    items: list[AIConversationRead]


class AssistantFeedbackRequest(BaseModel):
    message_id: int
    rating: Literal["good", "bad"]
    comment: str | None = Field(default=None, max_length=1000)


class AssistantFeedbackResponse(BaseModel):
    id: int
    message_id: int
    user_id: int | None
    rating: str
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIEvaluationRead(BaseModel):
    id: int
    created_at: datetime
    user_id: int | None
    question: str | None
    assistant_reply: str
    rating: str
    comment: str | None


class AIEvaluationListResponse(BaseModel):
    items: list[AIEvaluationRead]
    page: int
    limit: int
    total: int
    has_next: bool
