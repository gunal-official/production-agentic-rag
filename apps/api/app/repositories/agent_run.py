from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_run import AgentRun


class AgentRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        question: str,
    ) -> AgentRun:
        run = AgentRun(
            question=question,
            status="started",
        )

        self.session.add(run)

        await self.session.commit()
        await self.session.refresh(run)

        return run

    async def complete(
        self,
        run: AgentRun,
        answer: str,
        tool_name: str | None,
        retry_count: int,
        latency_ms: float,
        trace_data: list[dict],
    ) -> AgentRun:
        run.answer = answer
        run.tool_name = tool_name
        run.retry_count = retry_count
        run.latency_ms = latency_ms
        run.trace_data = trace_data
        run.status = "completed"

        await self.session.commit()
        await self.session.refresh(run)

        return run

    async def fail(
        self,
        run: AgentRun,
        error_message: str,
        latency_ms: float,
    ) -> AgentRun:
        run.status = "failed"
        run.error_message = error_message
        run.latency_ms = latency_ms

        await self.session.commit()
        await self.session.refresh(run)

        return run