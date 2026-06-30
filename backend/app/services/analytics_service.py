from datetime import date

from sqlalchemy.orm import Session

from app.repositories.analytics_repository import (
    get_assistant_feedback_counts,
    get_summary_counts,
    list_product_analytics,
    list_recent_bad_feedback,
    list_search_keyword_analytics,
)
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    AssistantFeedbackAnalyticsResponse,
    ProductAnalyticsItem,
    ProductAnalyticsResponse,
    RecentBadFeedbackItem,
    SearchKeywordAnalyticsItem,
    SearchKeywordAnalyticsResponse,
)


def get_admin_analytics_summary(db: Session) -> AnalyticsSummaryResponse:
    return AnalyticsSummaryResponse(**get_summary_counts(db))


def get_admin_search_keyword_analytics(
    db: Session,
    *,
    from_date: date | None,
    to_date: date | None,
    limit: int,
) -> SearchKeywordAnalyticsResponse:
    rows = list_search_keyword_analytics(db, from_date=from_date, to_date=to_date, limit=limit)
    return SearchKeywordAnalyticsResponse(
        items=[
            SearchKeywordAnalyticsItem(
                keyword=row.keyword,
                search_count=int(row.search_count),
                total_result_count=int(row.total_result_count),
                avg_result_count=float(row.avg_result_count),
            )
            for row in rows
        ]
    )


def get_admin_product_analytics(db: Session, *, limit: int) -> ProductAnalyticsResponse:
    rows = list_product_analytics(db, limit=limit)
    return ProductAnalyticsResponse(
        items=[
            ProductAnalyticsItem(
                product_id=row.product_id,
                name=row.name,
                category=row.category,
                click_count=int(row.click_count),
                favorite_count=int(row.favorite_count),
                assistant_recommendation_clicks=int(row.assistant_recommendation_clicks),
            )
            for row in rows
        ]
    )


def get_admin_assistant_feedback_analytics(db: Session, *, recent_limit: int) -> AssistantFeedbackAnalyticsResponse:
    good, bad = get_assistant_feedback_counts(db)
    total = good + bad
    recent_bad_feedback = [
        RecentBadFeedbackItem(
            message_id=row.message_id,
            comment=row.comment,
            created_at=row.created_at,
        )
        for row in list_recent_bad_feedback(db, limit=recent_limit)
    ]
    return AssistantFeedbackAnalyticsResponse(
        good=good,
        bad=bad,
        good_rate=round(good / total, 4) if total else 0.0,
        recent_bad_feedback=recent_bad_feedback,
    )
