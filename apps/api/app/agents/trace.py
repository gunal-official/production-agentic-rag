from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class TraceEvent:
    name: str
    started_at: float
    duration_ms: float
    metadata: dict = field(default_factory=dict)


class AgentTrace:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    async def run(
        self,
        name: str,
        func,
        **metadata,
    ):
        started = perf_counter()

        try:
            result = await func()

            return result

        finally:
            duration_ms = (
                perf_counter() - started
            ) * 1000

            self.events.append(
                TraceEvent(
                    name=name,
                    started_at=started,
                    duration_ms=duration_ms,
                    metadata=metadata,
                )
            )