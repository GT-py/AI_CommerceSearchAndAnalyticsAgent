from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import ProductListResponse, ProductRead
from app.services.product_service import get_product_or_404, get_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_public_products(
    keyword: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    sort: Literal["price_asc", "price_desc", "rating_desc", "newest"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> ProductListResponse:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price must be less than or equal to max_price",
        )

    return get_products(
        db,
        current_user=current_user,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_public_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)
