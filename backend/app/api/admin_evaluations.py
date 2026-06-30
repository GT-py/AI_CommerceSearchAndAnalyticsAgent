from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assistant import AIEvaluationListResponse
from app.services.assistant_service import get_admin_ai_evaluations

router = APIRouter(prefix="/admin/evaluations", tags=["admin-evaluations"])


@router.get("", response_model=AIEvaluationListResponse)
def list_ai_evaluations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> AIEvaluationListResponse:
    return get_admin_ai_evaluations(db, page=page, limit=limit)
