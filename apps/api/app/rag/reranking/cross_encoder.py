from sentence_transformers import CrossEncoder

from app.models.document import DocumentChunk


class CrossEncoderReranker:
    def __init__(self) -> None:
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L6-v2"
        )

    def rerank(
        self,
        query: str,
        chunks: list[tuple[DocumentChunk, str]],
        top_k: int,
    ):
        if not chunks:
            return []

        pairs = [
            (query, chunk.content)
            for chunk, _filename in chunks
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores, strict=True),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            (chunk, filename, float(score))
            for ((chunk, filename), score) in ranked[:top_k]
        ]