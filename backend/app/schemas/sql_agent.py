from typing import TypeAlias

from pydantic import BaseModel, Field

SQLAgentCell: TypeAlias = str | int | float | None


class SQLAgentQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class SQLAgentQueryResponse(BaseModel):
    intent: str
    description: str
    columns: list[str] = Field(default_factory=list)
    rows: list[list[SQLAgentCell]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
