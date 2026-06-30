from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battery_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    screen_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    category = relationship("Category", back_populates="products")
    favorites = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")
    click_logs = relationship("ClickLog", back_populates="product")
    product_features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
