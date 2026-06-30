from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.models.favorite import Favorite
from app.models.product import Product


def get_favorite(db: Session, *, user_id: int, product_id: int) -> Favorite | None:
    return db.scalar(
        select(Favorite)
        .options(joinedload(Favorite.product).joinedload(Product.category))
        .where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )


def list_favorites(db: Session, *, user_id: int) -> list[Favorite]:
    return list(
        db.scalars(
            select(Favorite)
            .options(joinedload(Favorite.product).joinedload(Product.category))
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        ).all()
    )


def create_favorite(db: Session, *, user_id: int, product_id: int) -> Favorite:
    favorite = Favorite(user_id=user_id, product_id=product_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return get_favorite(db, user_id=user_id, product_id=product_id) or favorite


def delete_favorite(db: Session, *, user_id: int, product_id: int) -> None:
    db.execute(delete(Favorite).where(Favorite.user_id == user_id, Favorite.product_id == product_id))
    db.commit()
