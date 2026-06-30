from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.user import User
from app.repositories.favorite_repository import (
    create_favorite,
    delete_favorite,
    get_favorite,
    list_favorites,
)
from app.repositories.product_repository import get_product
from app.schemas.favorite import FavoriteListResponse


def get_favorites_for_user(db: Session, current_user: User) -> FavoriteListResponse:
    return FavoriteListResponse(items=list_favorites(db, user_id=current_user.id))


def add_favorite_for_user(db: Session, current_user: User, product_id: int) -> Favorite:
    if get_product(db, product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing = get_favorite(db, user_id=current_user.id, product_id=product_id)
    if existing is not None:
        return existing

    try:
        return create_favorite(db, user_id=current_user.id, product_id=product_id)
    except IntegrityError:
        db.rollback()
        favorite = get_favorite(db, user_id=current_user.id, product_id=product_id)
        if favorite is not None:
            return favorite
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Favorite could not be created")


def remove_favorite_for_user(db: Session, current_user: User, product_id: int) -> dict[str, str]:
    delete_favorite(db, user_id=current_user.id, product_id=product_id)
    return {"message": "removed"}
