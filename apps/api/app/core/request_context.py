import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger("api.request")


async def request_context_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid4()),
    )

    started_at = perf_counter()

    response = await call_next(request)

    duration_ms = (
        perf_counter() - started_at
    ) * 1000

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={
            "request_id": request_id,
        },
    )

    return response