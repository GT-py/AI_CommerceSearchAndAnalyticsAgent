from sqlalchemy.orm import Session

from app.models.log import SearchLog


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
