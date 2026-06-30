from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ClickSource = Literal["search", "assistant", "favorite"]


class ClickLogCreate(BaseModel):
    product_id: int = Field(gt=0)
    source: ClickSource


class ClickLogResponse(BaseModel):
    id: int
    user_id: int | None
    product_id: int
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchLogRead(BaseModel):
    id: int
    user_id: int | None
    keyword: str | None
    category_id: int | None
    min_price: int | None
    max_price: int | None
    sort: str | None
    page: int
    limit: int
    result_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchLogListResponse(BaseModel):
    items: list[SearchLogRead]
    page: int
    limit: int
    total: int
    has_next: bool


class ClickLogProduct(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ClickLogRead(BaseModel):
    id: int
    user_id: int | None
    product_id: int
    product: ClickLogProduct
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClickLogListResponse(BaseModel):
    items: list[ClickLogRead]
    page: int
    limit: int
    total: int
    has_next: bool
