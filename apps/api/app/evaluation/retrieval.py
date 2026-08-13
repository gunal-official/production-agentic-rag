from app.schemas.search import SearchResult


def contains_expected_keyword(
    results: list[SearchResult],
    expected_keywords: list[str],
) -> bool:
    combined_content = " ".join(
        result.content.lower()
        for result in results
    )

    return any(
        keyword.lower() in combined_content
        for keyword in expected_keywords
    )


def reciprocal_rank(
    results: list[SearchResult],
    expected_keywords: list[str],
) -> float:
    for rank, result in enumerate(results, start=1):
        content = result.content.lower()

        if any(
            keyword.lower() in content
            for keyword in expected_keywords
        ):
            return 1.0 / rank

    return 0.0