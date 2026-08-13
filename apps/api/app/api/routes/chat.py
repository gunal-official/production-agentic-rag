from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSource,
)
from app.services.rag import RAGService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    service = RAGService(db)

    answer, results = await service.answer(
        question=request.question,
        top_k=request.top_k,
    )

    sources = [
        ChatSource(
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            filename=result.filename,
            page_number=result.page_number,
            chunk_index=result.chunk_index,
            content=result.content,
            similarity=result.similarity,
        )
        for result in results
    ]

    return ChatResponse(
        question=request.question,
        answer=answer,
        sources=sources,
    )