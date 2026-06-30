from sqlalchemy.orm import Session

from app.repositories.sql_agent_repository import (
    list_assistant_bad_feedback,
    list_category_search_counts,
    list_no_click_keywords,
    list_top_clicked_products,
    list_top_search_keywords,
)
from app.schemas.sql_agent import SQLAgentQueryRequest, SQLAgentQueryResponse

DEFAULT_LIMIT = 10

SUGGESTIONS = [
    "今月，最も検索されたキーワードは？",
    "クリック率が高い商品を上位10件出して",
    "検索されたがクリックされなかったキーワードを教えて",
]

FORBIDDEN_SQL_TOKENS = ["drop", "delete", "update", "insert", "alter", "truncate", ";", "--"]

INTENT_CONFIG = {
    "top_search_keywords": {
        "description": "検索回数が多いキーワードを上位順に集計しました。",
        "columns": ["keyword", "search_count"],
    },
    "top_clicked_products": {
        "description": "クリック数が多い商品を上位順に集計しました。",
        "columns": ["product_id", "product_name", "click_count"],
    },
    "no_click_keywords": {
        "description": "検索されたもののクリックにつながっていないキーワードを集計しました。",
        "columns": ["keyword", "search_count", "click_count"],
    },
    "category_search_counts": {
        "description": "カテゴリ別の検索回数を集計しました。",
        "columns": ["category_name", "search_count"],
    },
    "assistant_bad_feedback": {
        "description": "bad評価が付いたAI回答とコメントを新しい順に表示しました。",
        "columns": ["message_id", "question", "answer", "comment", "created_at"],
    },
}


def contains_forbidden_sql_token(question: str) -> bool:
    lowered = question.lower()
    return any(token in lowered for token in FORBIDDEN_SQL_TOKENS)


def classify_intent(question: str) -> str:
    normalized = question.lower()
    if contains_forbidden_sql_token(question):
        return "unknown"
    if "クリックされなかった" in question or "クリックにつながっていない" in question:
        return "no_click_keywords"
    if "カテゴリ" in question:
        return "category_search_counts"
    if "bad" in normalized or "不満" in question or "改善" in question:
        return "assistant_bad_feedback"
    if "クリック" in question or "人気商品" in question or "人気" in question:
        return "top_clicked_products"
    if "検索" in question and any(word in question for word in ["キーワード", "語句", "多い", "最も", "よく"]):
        return "top_search_keywords"
    return "unknown"


def unknown_response() -> SQLAgentQueryResponse:
    return SQLAgentQueryResponse(
        intent="unknown",
        description="対応していない質問です。次のような質問を試してください。",
        suggestions=SUGGESTIONS,
    )


def execute_sql_agent_query(db: Session, payload: SQLAgentQueryRequest) -> SQLAgentQueryResponse:
    intent = classify_intent(payload.question)
    if intent == "unknown":
        return unknown_response()

    if intent == "top_search_keywords":
        rows = [[row.keyword, int(row.search_count)] for row in list_top_search_keywords(db, limit=DEFAULT_LIMIT)]
    elif intent == "top_clicked_products":
        rows = [
            [row.product_id, row.product_name, int(row.click_count)]
            for row in list_top_clicked_products(db, limit=DEFAULT_LIMIT)
        ]
    elif intent == "no_click_keywords":
        rows = [
            [row.keyword, int(row.search_count), int(row.click_count)]
            for row in list_no_click_keywords(db, limit=DEFAULT_LIMIT)
        ]
    elif intent == "category_search_counts":
        rows = [
            [row.category_name, int(row.search_count)]
            for row in list_category_search_counts(db, limit=DEFAULT_LIMIT)
        ]
    elif intent == "assistant_bad_feedback":
        rows = [
            [
                row.message_id,
                row.question,
                row.answer,
                row.comment,
                row.created_at.isoformat(),
            ]
            for row in list_assistant_bad_feedback(db, limit=DEFAULT_LIMIT)
        ]
    else:
        return unknown_response()

    config = INTENT_CONFIG[intent]
    return SQLAgentQueryResponse(
        intent=intent,
        description=config["description"],
        columns=config["columns"],
        rows=rows,
    )
