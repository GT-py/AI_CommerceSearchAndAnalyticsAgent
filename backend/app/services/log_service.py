from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.log import ClickLog
from app.models.user import User
from app.repositories.log_repository import create_click_log, list_click_logs, list_search_logs
from app.repositories.product_repository import get_product
from app.schemas.log import (
    ClickLogCreate,
    ClickLogListResponse,
    SearchLogListResponse,
)


def create_click_log_entry(
    db: Session,
    *,
    payload: ClickLogCreate,
    current_user: User | None,
) -> ClickLog:
    if get_product(db, payload.product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return create_click_log(
        db,
        user_id=current_user.id if current_user else None,
        product_id=payload.product_id,
        source=payload.source,
    )


def get_admin_search_logs(db: Session, *, page: int, limit: int) -> SearchLogListResponse:
    items, total = list_search_logs(db, page=page, limit=limit)
    return SearchLogListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
        has_next=page * limit < total,
    )


def get_admin_click_logs(db: Session, *, page: int, limit: int) -> ClickLogListResponse:
    items, total = list_click_logs(db, page=page, limit=limit)
    return ClickLogListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
        has_next=page * limit < total,
    )
