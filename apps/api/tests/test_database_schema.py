import pytest
from sqlalchemy import text

from app.core.database import engine


@pytest.mark.asyncio
async def test_required_tables_exist():
    required_tables = {
        "documents",
        "document_chunks",
        "agent_runs",
        "tool_calls",
        "alembic_version",
    }

    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text(
                    """
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    """
                )
            )

            existing_tables = {
                row[0]
                for row in result.fetchall()
            }

        assert required_tables.issubset(
            existing_tables
        )

    finally:
        await engine.dispose()