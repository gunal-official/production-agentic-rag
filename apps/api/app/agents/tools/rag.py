from sqlalchemy.ext.asyncio import AsyncSession

from app.services.search import SearchService


class RAGTool:
    def __init__(self, session: AsyncSession):
        self.search_service = SearchService(session)

    async def run(
        self,
        query: str,
        top_k: int = 5,
    ):
        return await self.search_service.search(
            query=query,
            top_k=top_k,
        )