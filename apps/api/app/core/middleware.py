import asyncio

from fastapi import Request
from fastapi.responses import JSONResponse

REQUEST_TIMEOUT_SECONDS = 120.0


async def timeout_middleware(
    request: Request,
    call_next,
):
    try:
        return await asyncio.wait_for(
            call_next(request),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    except TimeoutError:
        return JSONResponse(
            status_code=504,
            content={
                "error": {
                    "code": "request_timeout",
                    "message": (
                        "The request exceeded the allowed time."
                    ),
                }
            },
        )