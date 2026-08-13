from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embeddings.local import LocalEmbeddingProvider
from app.rag.fusion import reciprocal_rank_fusion
from app.rag.reranking.cross_encoder import CrossEncoderReranker
from app.repositories.search import SearchRepository
from app.schemas.search import SearchResult


class SearchService:
    def __init__(self, session: AsyncSession):
        self.repository = SearchRepository(session)
        self.embedding_provider = LocalEmbeddingProvider()
        self.reranker = CrossEncoderReranker()

    async def search(
        self,
        query: str,
        top_k: int,
    ) -> list[SearchResult]:
        query_embedding = self.embedding_provider.embed_query(
            query
        )

        candidate_count = max(
            top_k * 4,
            20,
        )

        semantic_results = await self.repository.semantic_search(
            query_embedding=query_embedding,
            top_k=candidate_count,
        )

        keyword_results = await self.repository.keyword_search(
            query=query,
            top_k=candidate_count,
        )

        fused_chunks = reciprocal_rank_fusion(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
        )

        reranked = self.reranker.rerank(
            query=query,
            chunks=fused_chunks[:candidate_count],
            top_k=top_k,
        )

        results: list[SearchResult] = []

        for chunk, filename, score in reranked:
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    filename=filename,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    similarity=score,
                )
            )

        return results