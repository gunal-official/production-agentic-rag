from io import BytesIO

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import engine
from app.main import app


@pytest.mark.asyncio
async def test_upload_text_document():
    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/documents",
                files={
                    "file": (
                        "integration-test.txt",
                        BytesIO(
                            b"""
                            FastAPI is used for the backend API.
                            PostgreSQL stores application data.
                            pgvector stores document embeddings.
                            """
                        ),
                        "text/plain",
                    )
                },
            )

        assert response.status_code == 201

        data = response.json()

        assert data["filename"] == "integration-test.txt"
        assert data["content_type"] == "text/plain"
        assert data["status"] == "ready"

    finally:
        await engine.dispose()