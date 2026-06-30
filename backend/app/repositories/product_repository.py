from typing import Literal

from sqlalchemy import String, cast, delete, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.analytics import ProductFeature
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.log import ClickLog
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

ProductSort = Literal["price_asc", "price_desc", "rating_desc", "newest"]


def get_product(db: Session, product_id: int) -> Product | None:
    return db.scalar(
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.id == product_id)
    )


def list_products(
    db: Session,
    *,
    keyword: str | None,
    category_id: int | None,
    min_price: int | None,
    max_price: int | None,
    sort: ProductSort | None,
    page: int,
    limit: int,
) -> tuple[list[Product], int]:
    conditions = []
    if keyword:
        keyword_like = f"%{keyword}%"
        conditions.append(
            or_(
                Product.name.ilike(keyword_like),
                Product.description.ilike(keyword_like),
                Product.brand.ilike(keyword_like),
                cast(Product.tags, String).ilike(keyword_like),
                Category.name.ilike(keyword_like),
            )
        )
    if category_id is not None:
        conditions.append(Product.category_id == category_id)
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)

    total_stmt = select(func.count(Product.id)).join(Category)
    query_stmt = select(Product).options(joinedload(Product.category)).join(Category)
    if conditions:
        total_stmt = total_stmt.where(*conditions)
        query_stmt = query_stmt.where(*conditions)

    if sort == "price_asc":
        query_stmt = query_stmt.order_by(Product.price.asc(), Product.id.asc())
    elif sort == "price_desc":
        query_stmt = query_stmt.order_by(Product.price.desc(), Product.id.asc())
    elif sort == "rating_desc":
        query_stmt = query_stmt.order_by(Product.rating.desc().nullslast(), Product.id.asc())
    else:
        query_stmt = query_stmt.order_by(Product.created_at.desc(), Product.id.desc())

    offset = (page - 1) * limit
    total = db.scalar(total_stmt) or 0
    items = list(db.scalars(query_stmt.offset(offset).limit(limit)).all())
    return items, total


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return get_product(db, product.id) or product


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return get_product(db, product.id) or product


def delete_product(db: Session, product: Product) -> None:
    product_id = product.id
    db.execute(delete(Favorite).where(Favorite.product_id == product_id))
    db.execute(delete(ClickLog).where(ClickLog.product_id == product_id))
    db.execute(delete(ProductFeature).where(ProductFeature.product_id == product_id))
    db.delete(product)
    db.commit()
