from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    AssistantFeedbackAnalyticsResponse,
    ProductAnalyticsResponse,
    SearchKeywordAnalyticsResponse,
)
from app.services.analytics_service import (
    get_admin_analytics_summary,
    get_admin_assistant_feedback_analytics,
    get_admin_product_analytics,
    get_admin_search_keyword_analytics,
)

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> AnalyticsSummaryResponse:
    return get_admin_analytics_summary(db)


@router.get("/search-keywords", response_model=SearchKeywordAnalyticsResponse)
def search_keyword_analytics(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> SearchKeywordAnalyticsResponse:
    return get_admin_search_keyword_analytics(db, from_date=from_date, to_date=to_date, limit=limit)


@router.get("/products", response_model=ProductAnalyticsResponse)
def product_analytics(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> ProductAnalyticsResponse:
    return get_admin_product_analytics(db, limit=limit)


@router.get("/assistant-feedback", response_model=AssistantFeedbackAnalyticsResponse)
def assistant_feedback_analytics(
    recent_limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> AssistantFeedbackAnalyticsResponse:
    return get_admin_assistant_feedback_analytics(db, recent_limit=recent_limit)
