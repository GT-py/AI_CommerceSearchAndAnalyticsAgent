from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class DailySearchMetric(Base):
    __tablename__ = "daily_search_metrics"
    __table_args__ = (UniqueConstraint("date", "keyword", name="uq_daily_search_metrics_date_keyword"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    search_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    click_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    ctr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProductFeature(Base):
    __tablename__ = "product_features"
    __table_args__ = (UniqueConstraint("product_id", "date", name="uq_product_features_product_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    view_count_7d: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    click_count_7d: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    favorite_count_7d: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    ctr_7d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="product_features")
