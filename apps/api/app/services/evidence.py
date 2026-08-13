from app.schemas.search import SearchResult


class EvidenceService:
    def is_sufficient(
        self,
        results: list[SearchResult],
        minimum_score: float = 0.0,
    ) -> bool:
        if not results:
            return False

        top_result = results[0]

        return top_result.similarity > minimum_score