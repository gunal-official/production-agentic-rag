from uuid import UUID

from app.models.document import DocumentChunk


def reciprocal_rank_fusion(
    semantic_results,
    keyword_results,
    k: int = 60,
):
    scores: dict[UUID, float] = {}
    chunks: dict[UUID, tuple[DocumentChunk, str]] = {}

    for rank, (chunk, filename, _) in enumerate(
        semantic_results,
        start=1,
    ):
        chunks[chunk.id] = (
            chunk,
            filename,
        )

        scores[chunk.id] = (
            scores.get(
                chunk.id,
                0.0,
            )
            + 1.0 / (k + rank)
        )

    for rank, (chunk, filename, _) in enumerate(
        keyword_results,
        start=1,
    ):
        chunks[chunk.id] = (
            chunk,
            filename,
        )

        scores[chunk.id] = (
            scores.get(
                chunk.id,
                0.0,
            )
            + 1.0 / (k + rank)
        )

    ranked_ids = sorted(
        scores,
        key=lambda chunk_id: scores[chunk_id],
        reverse=True,
    )

    return [
        chunks[chunk_id]
        for chunk_id in ranked_ids
    ]