from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    question: str = Field(
        min_length=1,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class AgentSource(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: int | None
    chunk_index: int
    content: str
    similarity: float


class AgentResponse(BaseModel):
    question: str
    answer: str

    tool: str | None = None
    retry_count: int = 0

    trace: list[dict[str, Any]]

    sources: list[AgentSource]