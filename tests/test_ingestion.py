from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import DocumentChunk
from app.services.ingestion import create_document_with_chunks


def test_document_ingestion_creates_chunks(tmp_path):
    database_path = tmp_path / "test_ingestion.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    content = "A" * 1000

    with Session(engine) as session:
        document = create_document_with_chunks(
            session=session,
            title="Test Policy",
            content=content,
            department="Risk",
        )

        document_id = document.id

    with Session(engine) as session:
        chunks = session.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id
            )
            .order_by(DocumentChunk.chunk_index)
        ).all()

        assert len(chunks) == 2

        assert chunks[0].chunk_index == 0
        assert chunks[1].chunk_index == 1

        assert chunks[0].document_id == document_id
        assert chunks[1].document_id == document_id