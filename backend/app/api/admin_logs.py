from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.log import ClickLogListResponse, SearchLogListResponse
from app.services.log_service import get_admin_click_logs, get_admin_search_logs

router = APIRouter(prefix="/admin/logs", tags=["admin-logs"])


@router.get("/search", response_model=SearchLogListResponse)
def list_search_logs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> SearchLogListResponse:
    return get_admin_search_logs(db, page=page, limit=limit)


@router.get("/clicks", response_model=ClickLogListResponse)
def list_click_logs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> ClickLogListResponse:
    return get_admin_click_logs(db, page=page, limit=limit)
