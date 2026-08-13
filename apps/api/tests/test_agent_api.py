from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import engine
from app.main import app


@pytest.mark.asyncio
async def test_agent_calculator():
    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/agent",
                json={
                    "question": "25 * 4 + 10",
                    "top_k": 5,
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["answer"] == "110.0"
        assert data["tool"] == "calculator"

    finally:
        await engine.dispose()


@pytest.mark.asyncio
@patch(
    "app.agents.rag_agent.GroqProvider.generate",
    new_callable=AsyncMock,
)
async def test_agent_rag_with_mocked_llm(
    mock_generate: AsyncMock,
):
    try:
        mock_generate.return_value = (
            "Document embeddings are stored using pgvector. "
            "[Source 1]"
        )

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/agent",
                json={
                    "question": (
                        "What database stores document embeddings?"
                    ),
                    "top_k": 5,
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["tool"] == "rag"
        assert "pgvector" in data["answer"].lower()

    finally:
        await engine.dispose()