from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.rag.chunking.page_aware import chunk_pages
from app.rag.embeddings.local import LocalEmbeddingProvider
from app.rag.parsers.factory import ParserFactory
from app.repositories.document import DocumentRepository

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_DIR = Path("/tmp/uploads")


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.repository = DocumentRepository(session)
        self.embedding_provider = LocalEmbeddingProvider()

    async def upload_document(self, file: UploadFile) -> Document:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type",
            )

        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="File is too large",
            )

        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        original_name = file.filename or "unknown"
        suffix = Path(original_name).suffix.lower()

        stored_filename = f"{uuid4()}{suffix}"
        destination = UPLOAD_DIR / stored_filename

        destination.write_bytes(contents)

        document = await self.repository.create(
            filename=original_name,
            content_type=file.content_type or "application/octet-stream",
            source_path=str(destination),
        )

        try:
            await self.repository.update_status(
                document,
                "processing",
            )

            parser = ParserFactory.get_parser(
                file.content_type or ""
            )

            parsed = await parser.parse(
                str(destination)
            )

            text = parsed["text"]
            pages = parsed["pages"]

            if not text.strip():
                raise ValueError(
                    "No extractable text found in document"
                )

            chunks = chunk_pages(pages)

            if not chunks:
                raise ValueError(
                    "Document produced no chunks"
                )

            chunk_texts = [
                chunk["content"]
                for chunk in chunks
            ]

            embeddings = self.embedding_provider.embed_documents(
                chunk_texts
            )

            await self.repository.add_chunks(
                document=document,
                chunks=chunks,
                embeddings=embeddings,
            )

            document = await self.repository.update_status(
                document,
                "ready",
            )

            return document

        except Exception:
            await self.repository.update_status(
                document,
                "failed",
            )

            raise