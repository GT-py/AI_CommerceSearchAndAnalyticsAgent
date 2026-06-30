from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name.asc())).all())


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return db.scalar(select(Category).where(Category.slug == slug))


def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))


def category_has_products(db: Session, category_id: int) -> bool:
    count = db.scalar(select(func.count(Product.id)).where(Product.category_id == category_id))
    return bool(count)


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(name=payload.name, slug=payload.slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, payload: CategoryUpdate) -> Category:
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
