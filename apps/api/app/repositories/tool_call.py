from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tool_call import ToolCall


class ToolCallRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        agent_run_id,
        tool_name: str,
        input_data: dict | None = None,
    ) -> ToolCall:
        tool_call = ToolCall(
            agent_run_id=agent_run_id,
            tool_name=tool_name,
            input_data=input_data,
            status="started",
        )

        self.session.add(tool_call)

        await self.session.commit()
        await self.session.refresh(tool_call)

        return tool_call

    async def complete(
        self,
        tool_call: ToolCall,
        output_data: dict | None,
        latency_ms: float | None,
    ) -> ToolCall:
        tool_call.output_data = output_data
        tool_call.latency_ms = latency_ms
        tool_call.status = "completed"

        await self.session.commit()
        await self.session.refresh(tool_call)

        return tool_call

    async def fail(
        self,
        tool_call: ToolCall,
        error_message: str,
        latency_ms: float | None,
    ) -> ToolCall:
        tool_call.status = "failed"
        tool_call.error_message = error_message
        tool_call.latency_ms = latency_ms

        await self.session.commit()
        await self.session.refresh(tool_call)

        return tool_call