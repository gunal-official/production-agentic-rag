from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatSource(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: int | None
    chunk_index: int
    content: str
    similarity: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[ChatSource]