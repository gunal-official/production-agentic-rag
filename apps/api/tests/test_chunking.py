from app.rag.chunking.page_aware import chunk_pages


def test_page_aware_chunking():
    pages = [
        {
            "page_number": 1,
            "text": "A" * 1200,
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=500,
        overlap=100,
    )

    assert len(chunks) == 3
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["page_chunk_index"] == 0