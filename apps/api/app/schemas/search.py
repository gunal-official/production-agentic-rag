from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: int | None
    content: str
    chunk_index: int
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]