from typing import TypedDict


class EvaluationItem(TypedDict):
    question: str
    expected_keywords: list[str]


EVALUATION_DATASET: list[EvaluationItem] = [
    {
        "question": "What framework is used for the backend API?",
        "expected_keywords": ["FastAPI"],
    },
    {
        "question": "What database stores application data?",
        "expected_keywords": ["PostgreSQL"],
    },
    {
        "question": "What technology stores document embeddings?",
        "expected_keywords": ["pgvector"],
    },
    {
        "question": "What framework will coordinate agent workflows?",
        "expected_keywords": ["LangGraph"],
    },
]