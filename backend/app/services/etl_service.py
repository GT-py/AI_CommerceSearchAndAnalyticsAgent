from datetime import date

from sqlalchemy.orm import Session

from app.repositories.etl_repository import (
    list_daily_search_metrics,
    list_product_features,
    regenerate_daily_search_metrics,
    regenerate_product_features,
)
from app.schemas.etl import (
    DailySearchMetricListResponse,
    ETLRunResponse,
    ProductFeatureListResponse,
    ProductFeatureRead,
)


def run_etl(db: Session) -> ETLRunResponse:
    daily_count = regenerate_daily_search_metrics(db)
    feature_count = regenerate_product_features(db)
    db.commit()
    return ETLRunResponse(
        message="ETL completed",
        daily_search_metrics_count=daily_count,
        product_features_count=feature_count,
    )


def get_daily_search_metrics(
    db: Session,
    *,
    from_date: date | None,
    to_date: date | None,
    keyword: str | None,
    page: int,
    limit: int,
) -> DailySearchMetricListResponse:
    items, total = list_daily_search_metrics(
        db,
        from_date=from_date,
        to_date=to_date,
        keyword=keyword,
        page=page,
        limit=limit,
    )
    return DailySearchMetricListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
        has_next=page * limit < total,
    )


def get_product_features(
    db: Session,
    *,
    target_date: date | None,
    page: int,
    limit: int,
) -> ProductFeatureListResponse:
    items, total = list_product_features(db, target_date=target_date, page=page, limit=limit)
    return ProductFeatureListResponse(
        items=[
            ProductFeatureRead(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name if item.product else "",
                date=item.date,
                view_count_7d=item.view_count_7d,
                click_count_7d=item.click_count_7d,
                favorite_count_7d=item.favorite_count_7d,
                ctr_7d=item.ctr_7d,
                created_at=item.created_at,
            )
            for item in items
        ],
        page=page,
        limit=limit,
        total=total,
        has_next=page * limit < total,
    )
