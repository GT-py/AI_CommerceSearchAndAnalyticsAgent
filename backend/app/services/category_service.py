from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import (
    category_has_products,
    create_category,
    delete_category,
    get_category,
    get_category_by_name,
    get_category_by_slug,
    list_categories,
    update_category,
)
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_categories(db: Session) -> list[Category]:
    return list_categories(db)


def get_category_or_404(db: Session, category_id: int) -> Category:
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def ensure_category_unique(
    db: Session,
    *,
    name: str | None,
    slug: str | None,
    current_category_id: int | None = None,
) -> None:
    if name is not None:
        existing = get_category_by_name(db, name)
        if existing is not None and existing.id != current_category_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")
    if slug is not None:
        existing = get_category_by_slug(db, slug)
        if existing is not None and existing.id != current_category_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category slug already exists")


def create_category_for_admin(db: Session, payload: CategoryCreate) -> Category:
    ensure_category_unique(db, name=payload.name, slug=payload.slug)
    try:
        return create_category(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists") from exc


def update_category_for_admin(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
    category = get_category_or_404(db, category_id)
    values = payload.model_dump(exclude_unset=True)
    ensure_category_unique(
        db,
        name=values.get("name"),
        slug=values.get("slug"),
        current_category_id=category.id,
    )
    try:
        return update_category(db, category, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists") from exc


def delete_category_for_admin(db: Session, category_id: int) -> None:
    category = get_category_or_404(db, category_id)
    if category_has_products(db, category.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category has products and cannot be deleted",
        )
    delete_category(db, category)
