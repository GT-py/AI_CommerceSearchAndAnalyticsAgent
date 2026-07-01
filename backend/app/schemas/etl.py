from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ETLRunResponse(BaseModel):
    message: str
    daily_search_metrics_count: int
    product_features_count: int


class DailySearchMetricRead(BaseModel):
    id: int
    date: date
    keyword: str
    search_count: int
    click_count: int
    ctr: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailySearchMetricListResponse(BaseModel):
    items: list[DailySearchMetricRead]
    page: int
    limit: int
    total: int
    has_next: bool


class ProductFeatureRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    date: date
    view_count_7d: int
    click_count_7d: int
    favorite_count_7d: int
    ctr_7d: float
    created_at: datetime


class ProductFeatureListResponse(BaseModel):
    items: list[ProductFeatureRead]
    page: int
    limit: int
    total: int
    has_next: bool
