"""create initial tables

Revision ID: 0001_create_initial_tables
Revises:
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=True),
        sa.Column("weight_g", sa.Integer(), nullable=True),
        sa.Column("battery_hours", sa.Integer(), nullable=True),
        sa.Column("screen_size", sa.Float(), nullable=True),
        sa.Column("memory_gb", sa.Integer(), nullable=True),
        sa.Column("storage_gb", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_category_id"), "products", ["category_id"], unique=False)
    op.create_index(op.f("ix_products_price"), "products", ["price"], unique=False)

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_favorites_user_product"),
    )
    op.create_index(op.f("ix_favorites_id"), "favorites", ["id"], unique=False)
    op.create_index(op.f("ix_favorites_product_id"), "favorites", ["product_id"], unique=False)
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)

    op.create_table(
        "search_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("keyword", sa.String(length=255), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("min_price", sa.Integer(), nullable=True),
        sa.Column("max_price", sa.Integer(), nullable=True),
        sa.Column("sort", sa.String(length=50), nullable=True),
        sa.Column("page", sa.Integer(), server_default="1", nullable=False),
        sa.Column("limit", sa.Integer(), server_default="20", nullable=False),
        sa.Column("result_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_search_logs_id"), "search_logs", ["id"], unique=False)
    op.create_index(op.f("ix_search_logs_user_id"), "search_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_search_logs_keyword"), "search_logs", ["keyword"], unique=False)
    op.create_index(op.f("ix_search_logs_category_id"), "search_logs", ["category_id"], unique=False)

    op.create_table(
        "click_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=50), server_default="search", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_click_logs_id"), "click_logs", ["id"], unique=False)
    op.create_index(op.f("ix_click_logs_product_id"), "click_logs", ["product_id"], unique=False)
    op.create_index(op.f("ix_click_logs_user_id"), "click_logs", ["user_id"], unique=False)

    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_conversations_id"), "ai_conversations", ["id"], unique=False)
    op.create_index(op.f("ix_ai_conversations_user_id"), "ai_conversations", ["user_id"], unique=False)

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_messages_id"), "ai_messages", ["id"], unique=False)
    op.create_index(op.f("ix_ai_messages_conversation_id"), "ai_messages", ["conversation_id"], unique=False)

    op.create_table(
        "ai_response_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("rating", sa.String(length=20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["ai_messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_response_feedback_id"), "ai_response_feedback", ["id"], unique=False)
    op.create_index(op.f("ix_ai_response_feedback_message_id"), "ai_response_feedback", ["message_id"], unique=False)
    op.create_index(op.f("ix_ai_response_feedback_user_id"), "ai_response_feedback", ["user_id"], unique=False)

    op.create_table(
        "daily_search_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("search_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("click_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ctr", sa.Float(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "keyword", name="uq_daily_search_metrics_date_keyword"),
    )
    op.create_index(op.f("ix_daily_search_metrics_id"), "daily_search_metrics", ["id"], unique=False)
    op.create_index(op.f("ix_daily_search_metrics_date"), "daily_search_metrics", ["date"], unique=False)
    op.create_index(op.f("ix_daily_search_metrics_keyword"), "daily_search_metrics", ["keyword"], unique=False)

    op.create_table(
        "product_features",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("view_count_7d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("click_count_7d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("favorite_count_7d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ctr_7d", sa.Float(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "date", name="uq_product_features_product_date"),
    )
    op.create_index(op.f("ix_product_features_id"), "product_features", ["id"], unique=False)
    op.create_index(op.f("ix_product_features_product_id"), "product_features", ["product_id"], unique=False)
    op.create_index(op.f("ix_product_features_date"), "product_features", ["date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_product_features_date"), table_name="product_features")
    op.drop_index(op.f("ix_product_features_product_id"), table_name="product_features")
    op.drop_index(op.f("ix_product_features_id"), table_name="product_features")
    op.drop_table("product_features")
    op.drop_index(op.f("ix_daily_search_metrics_keyword"), table_name="daily_search_metrics")
    op.drop_index(op.f("ix_daily_search_metrics_date"), table_name="daily_search_metrics")
    op.drop_index(op.f("ix_daily_search_metrics_id"), table_name="daily_search_metrics")
    op.drop_table("daily_search_metrics")
    op.drop_index(op.f("ix_ai_response_feedback_user_id"), table_name="ai_response_feedback")
    op.drop_index(op.f("ix_ai_response_feedback_message_id"), table_name="ai_response_feedback")
    op.drop_index(op.f("ix_ai_response_feedback_id"), table_name="ai_response_feedback")
    op.drop_table("ai_response_feedback")
    op.drop_index(op.f("ix_ai_messages_conversation_id"), table_name="ai_messages")
    op.drop_index(op.f("ix_ai_messages_id"), table_name="ai_messages")
    op.drop_table("ai_messages")
    op.drop_index(op.f("ix_ai_conversations_user_id"), table_name="ai_conversations")
    op.drop_index(op.f("ix_ai_conversations_id"), table_name="ai_conversations")
    op.drop_table("ai_conversations")
    op.drop_index(op.f("ix_click_logs_user_id"), table_name="click_logs")
    op.drop_index(op.f("ix_click_logs_product_id"), table_name="click_logs")
    op.drop_index(op.f("ix_click_logs_id"), table_name="click_logs")
    op.drop_table("click_logs")
    op.drop_index(op.f("ix_search_logs_category_id"), table_name="search_logs")
    op.drop_index(op.f("ix_search_logs_keyword"), table_name="search_logs")
    op.drop_index(op.f("ix_search_logs_user_id"), table_name="search_logs")
    op.drop_index(op.f("ix_search_logs_id"), table_name="search_logs")
    op.drop_table("search_logs")
    op.drop_index(op.f("ix_favorites_user_id"), table_name="favorites")
    op.drop_index(op.f("ix_favorites_product_id"), table_name="favorites")
    op.drop_index(op.f("ix_favorites_id"), table_name="favorites")
    op.drop_table("favorites")
    op.drop_index(op.f("ix_products_price"), table_name="products")
    op.drop_index(op.f("ix_products_category_id"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
