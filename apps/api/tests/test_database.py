import pytest
from sqlalchemy import text

from app.core.database import engine


@pytest.mark.asyncio
async def test_database_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT 1")
            )

            assert result.scalar() == 1

    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_pgvector_extension():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT extname
                    FROM pg_extension
                    WHERE extname = 'vector'
                    """
                )
            )

            assert result.scalar() == "vector"

    finally:
        await engine.dispose()