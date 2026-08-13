from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        filename: str,
        content_type: str,
        source_path: str | None = None,
    ) -> Document:
        document = Document(
            filename=filename,
            content_type=content_type,
            source_path=source_path,
            status="uploaded",
        )

        self.session.add(document)

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def add_chunks(
        self,
        document: Document,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        for index, (chunk_data, embedding) in enumerate(
            zip(chunks, embeddings, strict=True)
        ):
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_data["content"],
                chunk_index=index,
                page_number=chunk_data.get("page_number"),
                extra_metadata={
                    "page_chunk_index": chunk_data.get(
                        "page_chunk_index"
                    ),
                },
                embedding=embedding,
            )

            self.session.add(chunk)

        await self.session.commit()

    async def update_status(
        self,
        document: Document,
        status: str,
    ) -> Document:
        document.status = status

        await self.session.commit()
        await self.session.refresh(document)

        return document