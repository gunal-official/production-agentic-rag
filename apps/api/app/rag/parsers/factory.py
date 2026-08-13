from app.rag.parsers.docx import DOCXParser
from app.rag.parsers.pdf import PDFParser
from app.rag.parsers.text import TextParser


class ParserFactory:
    @staticmethod
    def get_parser(content_type: str):
        if content_type in {
            "text/plain",
            "text/markdown",
        }:
            return TextParser()

        if content_type == "application/pdf":
            return PDFParser()

        if (
            content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            return DOCXParser()

        raise ValueError(
            f"No parser available for content type: {content_type}"
        )