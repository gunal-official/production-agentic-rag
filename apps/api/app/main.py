from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes.agent import router as agent_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.core.middleware import timeout_middleware
from app.core.observability import setup_observability
from app.core.rate_limit import limiter
from app.core.request_context import request_context_middleware

setup_logging()
setup_observability()


app = FastAPI(
    title="Enterprise Agentic RAG API",
    version="0.1.0",
    description="Production-grade Agentic RAG backend",
)


# ---------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,  # type: ignore[arg-type]
)

app.add_middleware(
    SlowAPIMiddleware,
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

app.middleware("http")(request_context_middleware)
app.middleware("http")(timeout_middleware)


# ---------------------------------------------------------
# API routes
# ---------------------------------------------------------

app.include_router(
    documents_router,
    prefix="/api/v1",
)

app.include_router(
    search_router,
    prefix="/api/v1",
)

app.include_router(
    chat_router,
    prefix="/api/v1",
)

app.include_router(
    agent_router,
    prefix="/api/v1",
)

app.include_router(
    health_router,
)


# ---------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------

@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": (
                    "An unexpected server error occurred."
                ),
            }
        },
    )


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Enterprise Agentic RAG API",
    }