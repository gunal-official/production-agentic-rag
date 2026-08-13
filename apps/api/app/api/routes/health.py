from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/live")
async def liveness():
    return {
        "status": "alive",
        "service": "agentic-rag-api",
    }


@router.get("/ready")
async def readiness(
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            text("SELECT 1")
        )

        if result.scalar() != 1:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "database": "unavailable",
                },
            )

        return {
            "status": "ready",
            "database": "connected",
        }

    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "unavailable",
            },
        )