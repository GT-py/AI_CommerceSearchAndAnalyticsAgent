from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.repositories.category_repository import get_category
from app.repositories.log_repository import create_search_log
from app.repositories.product_repository import (
    ProductSort,
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)
from app.schemas.product import ProductCreate, ProductListResponse, ProductUpdate

SortOption = Literal["price_asc", "price_desc", "rating_desc", "newest"]


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def get_products(
    db: Session,
    *,
    current_user: User | None,
    keyword: str | None,
    category_id: int | None,
    min_price: int | None,
    max_price: int | None,
    sort: ProductSort | None,
    page: int,
    limit: int,
) -> ProductListResponse:
    items, total = list_products(
        db,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
    )
    create_search_log(
        db,
        user_id=current_user.id if current_user else None,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
        result_count=total,
    )
    return ProductListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
        has_next=page * limit < total,
    )


def create_product_for_admin(db: Session, payload: ProductCreate) -> Product:
    if get_category(db, payload.category_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    try:
        return create_product(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product could not be created") from exc


def update_product_for_admin(db: Session, product_id: int, payload: ProductUpdate) -> Product:
    product = get_product_or_404(db, product_id)
    if payload.category_id is not None and get_category(db, payload.category_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    try:
        return update_product(db, product, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product could not be updated") from exc


def delete_product_for_admin(db: Session, product_id: int) -> None:
    product = get_product_or_404(db, product_id)
    delete_product(db, product)
