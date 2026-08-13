from pathlib import Path
from typing import Any


class TextParser:
    async def parse(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
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