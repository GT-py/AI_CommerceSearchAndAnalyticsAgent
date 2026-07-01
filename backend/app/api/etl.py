from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.etl import DailySearchMetricListResponse, ETLRunResponse, ProductFeatureListResponse
from app.services.etl_service import get_daily_search_metrics, get_product_features, run_etl

router = APIRouter(tags=["admin-etl"])


@router.post("/admin/etl/run", response_model=ETLRunResponse)
def run_admin_etl(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> ETLRunResponse:
    return run_etl(db)


@router.get("/admin/metrics/daily-search", response_model=DailySearchMetricListResponse)
def list_admin_daily_search_metrics(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> DailySearchMetricListResponse:
    return get_daily_search_metrics(
        db,
        from_date=from_date,
        to_date=to_date,
        keyword=keyword,
        page=page,
        limit=limit,
    )


@router.get("/admin/features/products", response_model=ProductFeatureListResponse)
def list_admin_product_features(
    date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> ProductFeatureListResponse:
    return get_product_features(db, target_date=date, page=page, limit=limit)
