from datetime import date
from typing import Any

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.models.ai import AIConversation, AIResponseFeedback
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.log import ClickLog, SearchLog
from app.models.product import Product
from app.models.user import User


def get_summary_counts(db: Session) -> dict[str, int]:
    good_feedback_count = db.scalar(
        select(func.count(AIResponseFeedback.id)).where(AIResponseFeedback.rating == "good")
    ) or 0
    bad_feedback_count = db.scalar(
        select(func.count(AIResponseFeedback.id)).where(AIResponseFeedback.rating == "bad")
    ) or 0

    return {
        "total_products": db.scalar(select(func.count(Product.id))) or 0,
        "total_users": db.scalar(select(func.count(User.id))) or 0,
        "total_searches": db.scalar(select(func.count(SearchLog.id))) or 0,
        "total_clicks": db.scalar(select(func.count(ClickLog.id))) or 0,
        "total_ai_conversations": db.scalar(select(func.count(AIConversation.id))) or 0,
        "total_ai_feedback": db.scalar(select(func.count(AIResponseFeedback.id))) or 0,
        "good_feedback_count": good_feedback_count,
        "bad_feedback_count": bad_feedback_count,
    }


def list_search_keyword_analytics(
    db: Session,
    *,
    from_date: date | None,
    to_date: date | None,
    limit: int,
) -> list[Any]:
    log_date = cast(SearchLog.created_at, Date)
    conditions = [
        SearchLog.keyword.is_not(None),
        func.length(func.trim(SearchLog.keyword)) > 0,
    ]
    if from_date is not None:
        conditions.append(log_date >= from_date)
    if to_date is not None:
        conditions.append(log_date <= to_date)

    stmt = (
        select(
            SearchLog.keyword.label("keyword"),
            func.count(SearchLog.id).label("search_count"),
            func.coalesce(func.sum(SearchLog.result_count), 0).label("total_result_count"),
            func.coalesce(func.avg(SearchLog.result_count), 0).label("avg_result_count"),
        )
        .where(*conditions)
        .group_by(SearchLog.keyword)
        .order_by(func.count(SearchLog.id).desc(), SearchLog.keyword.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def list_product_analytics(db: Session, *, limit: int) -> list[Any]:
    click_counts = (
        select(
            ClickLog.product_id.label("product_id"),
            func.count(ClickLog.id).label("click_count"),
            func.count(ClickLog.id)
            .filter(ClickLog.source == "assistant")
            .label("assistant_recommendation_clicks"),
        )
        .group_by(ClickLog.product_id)
        .subquery()
    )
    favorite_counts = (
        select(
            Favorite.product_id.label("product_id"),
            func.count(Favorite.id).label("favorite_count"),
        )
        .group_by(Favorite.product_id)
        .subquery()
    )

    click_count = func.coalesce(click_counts.c.click_count, 0)
    favorite_count = func.coalesce(favorite_counts.c.favorite_count, 0)
    assistant_click_count = func.coalesce(click_counts.c.assistant_recommendation_clicks, 0)

    stmt = (
        select(
            Product.id.label("product_id"),
            Product.name.label("name"),
            Category.name.label("category"),
            click_count.label("click_count"),
            favorite_count.label("favorite_count"),
            assistant_click_count.label("assistant_recommendation_clicks"),
        )
        .join(Category, Product.category_id == Category.id)
        .outerjoin(click_counts, Product.id == click_counts.c.product_id)
        .outerjoin(favorite_counts, Product.id == favorite_counts.c.product_id)
        .order_by(click_count.desc(), favorite_count.desc(), assistant_click_count.desc(), Product.id.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def get_assistant_feedback_counts(db: Session) -> tuple[int, int]:
    good = db.scalar(select(func.count(AIResponseFeedback.id)).where(AIResponseFeedback.rating == "good")) or 0
    bad = db.scalar(select(func.count(AIResponseFeedback.id)).where(AIResponseFeedback.rating == "bad")) or 0
    return good, bad


def list_recent_bad_feedback(db: Session, *, limit: int) -> list[Any]:
    stmt = (
        select(
            AIResponseFeedback.message_id.label("message_id"),
            AIResponseFeedback.comment.label("comment"),
            AIResponseFeedback.created_at.label("created_at"),
        )
        .where(AIResponseFeedback.rating == "bad")
        .order_by(AIResponseFeedback.created_at.desc(), AIResponseFeedback.id.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())
