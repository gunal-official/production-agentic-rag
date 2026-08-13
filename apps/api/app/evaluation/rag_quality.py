import asyncio
from dataclasses import dataclass

from app.core.database import AsyncSessionLocal
from app.services.rag import RAGService


@dataclass
class EvalCase:
    question: str
    expected_keywords: list[str]
    should_refuse: bool = False


CASES = [
    EvalCase(
        question="What database stores document embeddings?",
        expected_keywords=["postgresql", "pgvector"],
    ),
    EvalCase(
        question="What framework is used for the backend API?",
        expected_keywords=["fastapi"],
    ),
    EvalCase(
        question="Who won the FIFA World Cup in 1998?",
        expected_keywords=[],
        should_refuse=True,
    ),
]


REFUSAL_TEXT = (
    "I don't have enough information in the available documents."
)


async def run() -> None:
    passed = 0

    async with AsyncSessionLocal() as session:
        rag = RAGService(session)

        for case in CASES:
            answer, sources = await rag.answer(
                question=case.question,
                top_k=5,
            )

            normalized = answer.lower()

            if case.should_refuse:
                ok = REFUSAL_TEXT.lower() in normalized
            else:
                keyword_ok = all(
                    keyword.lower() in normalized
                    for keyword in case.expected_keywords
                )

                citation_ok = "[source" in normalized

                source_ok = len(sources) > 0

                ok = keyword_ok and citation_ok and source_ok

            passed += int(ok)

            print("=" * 70)
            print("Question:", case.question)
            print("Answer:", answer)
            print("Sources:", len(sources))
            print("PASS:", ok)

    print()
    print("=" * 70)
    print(f"Passed: {passed}/{len(CASES)}")
    print(
        f"Pass Rate: {passed / len(CASES):.2%}"
    )


if __name__ == "__main__":
    asyncio.run(run())