from typing import Any, TypedDict

from app.schemas.search import SearchResult


class AgentState(TypedDict, total=False):
    question: str
    retrieval_query: str
    top_k: int

    tool_name: str
    tool_result: str

    needs_retrieval: bool
    search_results: list[SearchResult]

    evidence_valid: bool

    answer: str
    retry_count: int

    trace: list[dict[str, Any]]