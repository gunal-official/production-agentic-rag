from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.groq_provider import GroqProvider
from app.services.search import SearchService


class RAGService:
    def __init__(self, session: AsyncSession):
        self.search_service = SearchService(session)
        self.llm = GroqProvider()

    async def answer(
        self,
        question: str,
        top_k: int,
    ):
        results = await self.search_service.search(
            query=question,
            top_k=top_k,
        )

        if not results:
            return (
                "I don't have enough information in the available documents.",
                [],
            )

        context_parts: list[str] = []

        for index, result in enumerate(results, start=1):
            page_label = (
                f"page {result.page_number}"
                if result.page_number is not None
                else "page unavailable"
            )

            context_parts.append(
                "\n".join(
                    [
                        f"[Source {index}]",
                        f"File: {result.filename}",
                        f"Location: {page_label}",
                        f"Content: {result.content}",
                    ]
                )
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a grounded enterprise knowledge assistant.

Answer the user's question using ONLY the provided sources.

RULES:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Every factual claim must be supported by the provided sources.
4. Cite supporting evidence using [Source N].
5. Use the exact source numbers provided.
6. Never invent a source number.
7. If multiple sources support a statement, cite them together.
8. If the sources do not contain enough information, answer exactly:
   "I don't have enough information in the available documents."
9. Keep the answer concise and factual.

SOURCES:

{context}

QUESTION:

{question}

ANSWER:
""".strip()

        answer = await self.llm.generate(prompt)

        return answer, results