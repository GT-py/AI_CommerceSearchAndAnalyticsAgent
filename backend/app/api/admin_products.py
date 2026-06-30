from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import (
    create_product_for_admin,
    delete_product_for_admin,
    update_product_for_admin,
)

router = APIRouter(prefix="/admin/products", tags=["admin-products"])


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return create_product_for_admin(db, payload)


@router.patch("/{product_id}", response_model=ProductRead)
def patch_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return update_product_for_admin(db, product_id, payload)


@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> dict[str, str]:
    delete_product_for_admin(db, product_id)
    return {"message": "deleted"}
