import asyncio

from app.core.database import AsyncSessionLocal
from app.evaluation.dataset import EVALUATION_DATASET
from app.evaluation.retrieval import (
    contains_expected_keyword,
    reciprocal_rank,
)
from app.services.search import SearchService


async def run_evaluation() -> None:
    total = len(EVALUATION_DATASET)

    hits = 0
    reciprocal_rank_sum = 0.0

    async with AsyncSessionLocal() as session:
        search_service = SearchService(session)

        for item in EVALUATION_DATASET:
            question = item["question"]
            expected_keywords = item["expected_keywords"]

            results = await search_service.search(
                query=question,
                top_k=5,
            )

            hit = contains_expected_keyword(
                results,
                expected_keywords,
            )

            rr = reciprocal_rank(
                results,
                expected_keywords,
            )

            if hit:
                hits += 1

            reciprocal_rank_sum += rr

            print("=" * 70)
            print("Question:", question)
            print("Expected:", expected_keywords)
            print("Hit:", hit)
            print("Reciprocal Rank:", round(rr, 4))

            if results:
                print(
                    "Top result:",
                    results[0].content[:200],
                )

    hit_rate = hits / total if total else 0
    mrr = reciprocal_rank_sum / total if total else 0

    print()
    print("=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    print(f"Questions: {total}")
    print(f"Hits: {hits}")
    print(f"Hit Rate@5: {hit_rate:.2%}")
    print(f"MRR: {mrr:.4f}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())