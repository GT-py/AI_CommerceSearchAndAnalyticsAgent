from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.product import ProductRead


class FavoriteRead(BaseModel):
    id: int
    product: ProductRead
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FavoriteListResponse(BaseModel):
    items: list[FavoriteRead]
