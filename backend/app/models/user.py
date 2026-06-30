from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", server_default="user")

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    search_logs = relationship("SearchLog", back_populates="user")
    click_logs = relationship("ClickLog", back_populates="user")
    ai_conversations = relationship("AIConversation", back_populates="user")
    ai_response_feedback = relationship("AIResponseFeedback", back_populates="user")
