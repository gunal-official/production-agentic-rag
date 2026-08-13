from pathlib import Path
from typing import Any

from docx import Document


class DOCXParser:
    async def parse(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        document = Document(str(path))

        text = "\n\n".join(
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        return {
            "text": text,
            "pages": [
                {
                    "page_number": None,
                    "text": text,
                }
            ],
        }