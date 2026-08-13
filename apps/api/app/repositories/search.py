from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int,
    ):
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        statement = (
            select(
                DocumentChunk,
                Document.filename,
                distance.label("distance"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )

        result = await self.session.execute(statement)

        return result.all()

    async def keyword_search(
        self,
        query: str,
        top_k: int,
    ):
        search_vector = func.to_tsvector(
            "english",
            DocumentChunk.content,
        )

        search_query = func.plainto_tsquery(
            "english",
            query,
        )

        rank = func.ts_rank(
            search_vector,
            search_query,
        )

        statement = (
            select(
                DocumentChunk,
                Document.filename,
                rank.label("rank"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(search_vector.op("@@")(search_query))
            .order_by(rank.desc())
            .limit(top_k)
        )

        result = await self.session.execute(statement)

        return result.all()