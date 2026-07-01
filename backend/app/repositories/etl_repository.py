from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import Date, delete, func, select, cast
from sqlalchemy.orm import Session, joinedload

from app.models.analytics import DailySearchMetric, ProductFeature
from app.models.favorite import Favorite
from app.models.log import ClickLog, SearchLog
from app.models.product import Product


def regenerate_daily_search_metrics(db: Session) -> int:
    search_date = cast(SearchLog.created_at, Date)
    search_rows = list(
        db.execute(
            select(
                search_date.label("date"),
                SearchLog.keyword.label("keyword"),
                func.count(SearchLog.id).label("search_count"),
            )
            .where(
                SearchLog.keyword.is_not(None),
                func.length(func.trim(SearchLog.keyword)) > 0,
            )
            .group_by(search_date, SearchLog.keyword)
            .order_by(search_date.asc(), SearchLog.keyword.asc())
        ).all()
    )

    if not search_rows:
        return 0

    target_dates = sorted({row.date for row in search_rows})
    db.execute(delete(DailySearchMetric).where(DailySearchMetric.date.in_(target_dates)))

    click_date = cast(ClickLog.created_at, Date)
    click_rows = list(
        db.execute(
            select(click_date.label("date"), func.count(ClickLog.id).label("click_count"))
            .where(click_date.in_(target_dates))
            .group_by(click_date)
        ).all()
    )
    click_counts = {row.date: int(row.click_count) for row in click_rows}

    metrics: list[DailySearchMetric] = []
    for row in search_rows:
        search_count = int(row.search_count)
        click_count = click_counts.get(row.date, 0)
        metrics.append(
            DailySearchMetric(
                date=row.date,
                keyword=row.keyword,
                search_count=search_count,
                click_count=click_count,
                ctr=click_count / search_count if search_count else 0.0,
            )
        )

    db.add_all(metrics)
    db.flush()
    return len(metrics)


def regenerate_product_features(db: Session, *, run_date: date | None = None) -> int:
    target_date = run_date or date.today()
    start_date = target_date - timedelta(days=6)
    start_at = datetime.combine(start_date, time.min)
    end_at = datetime.combine(target_date + timedelta(days=1), time.min)

    db.execute(delete(ProductFeature).where(ProductFeature.date == target_date))

    click_rows = list(
        db.execute(
            select(ClickLog.product_id, func.count(ClickLog.id).label("click_count"))
            .where(ClickLog.created_at >= start_at, ClickLog.created_at < end_at)
            .group_by(ClickLog.product_id)
        ).all()
    )
    favorite_rows = list(
        db.execute(
            select(Favorite.product_id, func.count(Favorite.id).label("favorite_count"))
            .where(Favorite.created_at >= start_at, Favorite.created_at < end_at)
            .group_by(Favorite.product_id)
        ).all()
    )
    click_counts = {row.product_id: int(row.click_count) for row in click_rows}
    favorite_counts = {row.product_id: int(row.favorite_count) for row in favorite_rows}

    product_ids = list(db.scalars(select(Product.id).order_by(Product.id.asc())).all())
    features: list[ProductFeature] = []
    for product_id in product_ids:
        click_count = click_counts.get(product_id, 0)
        view_count = click_count
        favorite_count = favorite_counts.get(product_id, 0)
        features.append(
            ProductFeature(
                product_id=product_id,
                date=target_date,
                view_count_7d=view_count,
                click_count_7d=click_count,
                favorite_count_7d=favorite_count,
                ctr_7d=click_count / max(view_count, 1),
            )
        )

    db.add_all(features)
    db.flush()
    return len(features)


def list_daily_search_metrics(
    db: Session,
    *,
    from_date: date | None,
    to_date: date | None,
    keyword: str | None,
    page: int,
    limit: int,
) -> tuple[list[DailySearchMetric], int]:
    conditions = []
    if from_date is not None:
        conditions.append(DailySearchMetric.date >= from_date)
    if to_date is not None:
        conditions.append(DailySearchMetric.date <= to_date)
    if keyword:
        conditions.append(DailySearchMetric.keyword.ilike(f"%{keyword}%"))

    total_stmt = select(func.count(DailySearchMetric.id))
    query_stmt = select(DailySearchMetric)
    if conditions:
        total_stmt = total_stmt.where(*conditions)
        query_stmt = query_stmt.where(*conditions)

    offset = (page - 1) * limit
    total = db.scalar(total_stmt) or 0
    items = list(
        db.scalars(
            query_stmt
            .order_by(DailySearchMetric.date.desc(), DailySearchMetric.search_count.desc(), DailySearchMetric.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return items, total


def list_product_features(
    db: Session,
    *,
    target_date: date | None,
    page: int,
    limit: int,
) -> tuple[list[ProductFeature], int]:
    conditions = []
    if target_date is not None:
        conditions.append(ProductFeature.date == target_date)

    total_stmt = select(func.count(ProductFeature.id))
    query_stmt = select(ProductFeature).options(joinedload(ProductFeature.product).load_only(Product.id, Product.name))
    if conditions:
        total_stmt = total_stmt.where(*conditions)
        query_stmt = query_stmt.where(*conditions)

    offset = (page - 1) * limit
    total = db.scalar(total_stmt) or 0
    items = list(
        db.scalars(
            query_stmt
            .order_by(ProductFeature.date.desc(), ProductFeature.click_count_7d.desc(), ProductFeature.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return items, total
