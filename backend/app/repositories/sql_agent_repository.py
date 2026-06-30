from typing import Any

from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models.ai import AIMessage, AIResponseFeedback
from app.models.category import Category
from app.models.log import ClickLog, SearchLog
from app.models.product import Product


def list_top_search_keywords(db: Session, *, limit: int) -> list[Any]:
    stmt = (
        select(
            SearchLog.keyword.label("keyword"),
            func.count(SearchLog.id).label("search_count"),
        )
        .where(
            SearchLog.keyword.is_not(None),
            func.length(func.trim(SearchLog.keyword)) > 0,
        )
        .group_by(SearchLog.keyword)
        .order_by(func.count(SearchLog.id).desc(), SearchLog.keyword.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def list_top_clicked_products(db: Session, *, limit: int) -> list[Any]:
    stmt = (
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.count(ClickLog.id).label("click_count"),
        )
        .join(ClickLog, ClickLog.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.count(ClickLog.id).desc(), Product.id.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def list_no_click_keywords(db: Session, *, limit: int) -> list[Any]:
    search_keywords = (
        select(
            SearchLog.keyword.label("keyword"),
            func.count(SearchLog.id).label("search_count"),
        )
        .where(
            SearchLog.keyword.is_not(None),
            func.length(func.trim(SearchLog.keyword)) > 0,
        )
        .group_by(SearchLog.keyword)
        .subquery()
    )

    keyword_pattern = func.concat("%", search_keywords.c.keyword, "%")
    product_matches_keyword = or_(
        Product.name.ilike(keyword_pattern),
        Product.description.ilike(keyword_pattern),
        Product.brand.ilike(keyword_pattern),
        cast(Product.tags, String).ilike(keyword_pattern),
    )

    click_count = func.count(ClickLog.id)
    stmt = (
        select(
            search_keywords.c.keyword.label("keyword"),
            search_keywords.c.search_count.label("search_count"),
            click_count.label("click_count"),
        )
        .select_from(search_keywords)
        .outerjoin(Product, product_matches_keyword)
        .outerjoin(ClickLog, and_(ClickLog.product_id == Product.id, ClickLog.source == "search"))
        .group_by(search_keywords.c.keyword, search_keywords.c.search_count)
        .having(click_count == 0)
        .order_by(search_keywords.c.search_count.desc(), search_keywords.c.keyword.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def list_category_search_counts(db: Session, *, limit: int) -> list[Any]:
    stmt = (
        select(
            Category.name.label("category_name"),
            func.count(SearchLog.id).label("search_count"),
        )
        .join(SearchLog, SearchLog.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .order_by(func.count(SearchLog.id).desc(), Category.id.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def list_assistant_bad_feedback(db: Session, *, limit: int) -> list[Any]:
    user_message = aliased(AIMessage)
    question_subquery = (
        select(user_message.content)
        .where(
            user_message.conversation_id == AIMessage.conversation_id,
            user_message.role == "user",
            user_message.id < AIMessage.id,
        )
        .order_by(user_message.id.desc())
        .limit(1)
        .scalar_subquery()
    )

    stmt = (
        select(
            AIResponseFeedback.message_id.label("message_id"),
            question_subquery.label("question"),
            AIMessage.content.label("answer"),
            AIResponseFeedback.comment.label("comment"),
            AIResponseFeedback.created_at.label("created_at"),
        )
        .join(AIMessage, AIResponseFeedback.message_id == AIMessage.id)
        .where(AIResponseFeedback.rating == "bad")
        .order_by(AIResponseFeedback.created_at.desc(), AIResponseFeedback.id.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())
