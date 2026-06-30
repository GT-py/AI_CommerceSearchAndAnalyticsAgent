from datetime import datetime

from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    total_products: int
    total_users: int
    total_searches: int
    total_clicks: int
    total_ai_conversations: int
    total_ai_feedback: int
    good_feedback_count: int
    bad_feedback_count: int


class SearchKeywordAnalyticsItem(BaseModel):
    keyword: str
    search_count: int
    total_result_count: int
    avg_result_count: float


class SearchKeywordAnalyticsResponse(BaseModel):
    items: list[SearchKeywordAnalyticsItem]


class ProductAnalyticsItem(BaseModel):
    product_id: int
    name: str
    category: str
    click_count: int
    favorite_count: int
    assistant_recommendation_clicks: int


class ProductAnalyticsResponse(BaseModel):
    items: list[ProductAnalyticsItem]


class RecentBadFeedbackItem(BaseModel):
    message_id: int
    comment: str | None
    created_at: datetime


class AssistantFeedbackAnalyticsResponse(BaseModel):
    good: int
    bad: int
    good_rate: float
    recent_bad_feedback: list[RecentBadFeedbackItem]
