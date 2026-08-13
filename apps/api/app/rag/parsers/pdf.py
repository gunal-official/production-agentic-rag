from pathlib import Path
from typing import Any

from pypdf import PdfReader


class PDFParser:
    async def parse(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        reader = PdfReader(path)

        pages: list[dict[str, Any]] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if text:
                pages.append(
                    {
                        "page_number": page_number,
                        "text": text,
                    }
                )

        full_text = "\n\n".join(
            page["text"] for page in pages
        )

        return {
            "text": full_text,
            "pages": pages,
        }