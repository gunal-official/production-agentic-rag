from typing import Any


def chunk_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []

    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text", "")

        if not text.strip():
            continue

        start = 0
        text_length = len(text)
        page_chunk_index = 0

        while start < text_length:
            end = start + chunk_size

            content = text[start:end].strip()

            if content:
                chunks.append(
                    {
                        "content": content,
                        "page_number": page_number,
                        "page_chunk_index": page_chunk_index,
                    }
                )

                page_chunk_index += 1

            start += chunk_size - overlap

    return chunks