from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.sql_agent import SQLAgentQueryRequest, SQLAgentQueryResponse
from app.services.sql_agent_service import execute_sql_agent_query

router = APIRouter(prefix="/admin/sql-agent", tags=["admin-sql-agent"])


@router.post("/query", response_model=SQLAgentQueryResponse)
def query_sql_agent(
    payload: SQLAgentQueryRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> SQLAgentQueryResponse:
    return execute_sql_agent_query(db, payload)
