"""change embedding dimension to 384

Revision ID: a21ad88c9ad6
Revises: 7deb32b3d775
Create Date: 2026-08-13 01:03:05.509550
"""

from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector


revision: str = "a21ad88c9ad6"
down_revision: Union[str, Sequence[str], None] = "7deb32b3d775"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "document_chunks",
        "embedding",
        existing_type=Vector(1536),
        type_=Vector(384),
        existing_nullable=True,
        postgresql_using="embedding::vector(384)",
    )


def downgrade() -> None:
    op.alter_column(
        "document_chunks",
        "embedding",
        existing_type=Vector(384),
        type_=Vector(1536),
        existing_nullable=True,
        postgresql_using="embedding::vector(1536)",
    )