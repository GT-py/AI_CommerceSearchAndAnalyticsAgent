from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.favorite import FavoriteListResponse, FavoriteRead
from app.services.favorite_service import (
    add_favorite_for_user,
    get_favorites_for_user,
    remove_favorite_for_user,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=FavoriteListResponse)
def list_my_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteListResponse:
    return get_favorites_for_user(db, current_user)


@router.post("/{product_id}", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
def add_my_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_favorite_for_user(db, current_user, product_id)


@router.delete("/{product_id}")
def remove_my_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return remove_favorite_for_user(db, current_user, product_id)
