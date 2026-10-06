from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.services.chunking import chunk_text


def create_document_with_chunks(
    session: Session,
    title: str,
    content: str,
    department: str = "General",
) -> Document:
    """
    Create a document and persist its text chunks.
    """

    document = Document(
        title=title,
        content=content,
        department=department,
    )

    session.add(document)

    # We need the document ID before creating its chunks.
    session.flush()

    chunks = chunk_text(content)

    document_chunks = [
        DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
        )
        for index, chunk in enumerate(chunks)
    ]

    session.add_all(document_chunks)

    session.commit()
    session.refresh(document)

    return document