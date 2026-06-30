from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.log import ClickLog, SearchLog
from app.models.product import Product


def create_search_log(
    db: Session,
    *,
    user_id: int | None,
    keyword: str | None,
    category_id: int | None,
    min_price: int | None,
    max_price: int | None,
    sort: str | None,
    page: int,
    limit: int,
    result_count: int,
) -> SearchLog:
    search_log = SearchLog(
        user_id=user_id,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
        result_count=result_count,
    )
    db.add(search_log)
    db.commit()
    db.refresh(search_log)
    return search_log


def create_click_log(
    db: Session,
    *,
    user_id: int | None,
    product_id: int,
    source: str,
) -> ClickLog:
    click_log = ClickLog(user_id=user_id, product_id=product_id, source=source)
    db.add(click_log)
    db.commit()
    db.refresh(click_log)
    return click_log


def list_search_logs(db: Session, *, page: int, limit: int) -> tuple[list[SearchLog], int]:
    total = db.scalar(select(func.count(SearchLog.id))) or 0
    offset = (page - 1) * limit
    items = list(
        db.scalars(
            select(SearchLog)
            .order_by(SearchLog.created_at.desc(), SearchLog.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return items, total


def list_click_logs(db: Session, *, page: int, limit: int) -> tuple[list[ClickLog], int]:
    total = db.scalar(select(func.count(ClickLog.id))) or 0
    offset = (page - 1) * limit
    items = list(
        db.scalars(
            select(ClickLog)
            .options(joinedload(ClickLog.product).load_only(Product.id, Product.name))
            .order_by(ClickLog.created_at.desc(), ClickLog.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return items, total
