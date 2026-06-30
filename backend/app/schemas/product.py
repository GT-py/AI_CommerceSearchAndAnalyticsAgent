from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryRead


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    category_id: int
    brand: str | None = Field(default=None, max_length=100)
    price: int = Field(ge=0)
    rating: float | None = Field(default=None, ge=0, le=5)
    stock: int | None = Field(default=None, ge=0)
    weight_g: int | None = Field(default=None, ge=0)
    battery_hours: int | None = Field(default=None, ge=0)
    screen_size: float | None = Field(default=None, ge=0)
    memory_gb: int | None = Field(default=None, ge=0)
    storage_gb: int | None = Field(default=None, ge=0)
    tags: list[str] = Field(default_factory=list)
    thumbnail_url: str | None = Field(default=None, max_length=500)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    category_id: int | None = None
    brand: str | None = Field(default=None, max_length=100)
    price: int | None = Field(default=None, ge=0)
    rating: float | None = Field(default=None, ge=0, le=5)
    stock: int | None = Field(default=None, ge=0)
    weight_g: int | None = Field(default=None, ge=0)
    battery_hours: int | None = Field(default=None, ge=0)
    screen_size: float | None = Field(default=None, ge=0)
    memory_gb: int | None = Field(default=None, ge=0)
    storage_gb: int | None = Field(default=None, ge=0)
    tags: list[str] | None = None
    thumbnail_url: str | None = Field(default=None, max_length=500)


class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    category: CategoryRead
    brand: str | None
    price: int
    rating: float | None
    stock: int | None
    weight_g: int | None
    battery_hours: int | None
    screen_size: float | None
    memory_gb: int | None
    storage_gb: int | None
    tags: list[str]
    thumbnail_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    page: int
    limit: int
    total: int
    has_next: bool
