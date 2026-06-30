from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import (
    create_category_for_admin,
    delete_category_for_admin,
    get_categories,
    update_category_for_admin,
)

router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[CategoryRead])
def list_public_categories(db: Session = Depends(get_db)):
    return get_categories(db)


@router.post("/admin/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return create_category_for_admin(db, payload)


@router.patch("/admin/categories/{category_id}", response_model=CategoryRead)
def patch_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return update_category_for_admin(db, category_id, payload)


@router.delete("/admin/categories/{category_id}")
def remove_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> dict[str, str]:
    delete_category_for_admin(db, category_id)
    return {"message": "deleted"}
