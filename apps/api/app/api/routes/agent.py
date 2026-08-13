from time import perf_counter

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.rag_agent import AgenticRAG
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.repositories.agent_run import AgentRunRepository
from app.repositories.tool_call import ToolCallRepository
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
    AgentSource,
)

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post(
    "",
    response_model=AgentResponse,
)
@limiter.limit("20/minute")
async def run_agent(
    request: Request,
    payload: AgentRequest,
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    started_at = perf_counter()

    run_repository = AgentRunRepository(db)
    tool_repository = ToolCallRepository(db)

    run_record = await run_repository.create(
        question=payload.question,
    )

    try:
        agent = AgenticRAG(db)

        result = await agent.run(
            question=payload.question,
            top_k=payload.top_k,
        )

        search_results = result.get(
            "search_results",
            [],
        )

        sources = [
            AgentSource(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                filename=item.filename,
                page_number=item.page_number,
                chunk_index=item.chunk_index,
                content=item.content,
                similarity=item.similarity,
            )
            for item in search_results
        ]

        answer = result.get(
            "answer",
            "I don't have enough information "
            "in the available documents.",
        )

        latency_ms = (
            perf_counter() - started_at
        ) * 1000

        await run_repository.complete(
            run=run_record,
            answer=answer,
            tool_name=result.get("tool_name"),
            retry_count=result.get(
                "retry_count",
                0,
            ),
            latency_ms=latency_ms,
            trace_data=result.get(
                "trace",
                [],
            ),
        )

        tool_name = result.get("tool_name")

        if tool_name:
            tool_call = await tool_repository.create(
                agent_run_id=run_record.id,
                tool_name=tool_name,
                input_data={
                    "question": payload.question,
                    "top_k": payload.top_k,
                },
            )

            await tool_repository.complete(
                tool_call=tool_call,
                output_data={
                    "answer": answer,
                    "source_count": len(sources),
                },
                latency_ms=latency_ms,
            )

        return AgentResponse(
            question=payload.question,
            answer=answer,
            tool=tool_name,
            retry_count=result.get(
                "retry_count",
                0,
            ),
            trace=result.get(
                "trace",
                [],
            ),
            sources=sources,
        )

    except Exception as exc:
        latency_ms = (
            perf_counter() - started_at
        ) * 1000

        await run_repository.fail(
            run=run_record,
            error_message=str(exc),
            latency_ms=latency_ms,
        )

        raise