from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.log import ClickLogCreate, ClickLogResponse
from app.services.log_service import create_click_log_entry

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/click", response_model=ClickLogResponse, status_code=status.HTTP_201_CREATED)
def create_click_log(
    payload: ClickLogCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return create_click_log_entry(db, payload=payload, current_user=current_user)
