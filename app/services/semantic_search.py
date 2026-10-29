import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.services.embeddings import generate_embedding


def cosine_similarity(vector_a, vector_b):
    """
    Calculate how similar two vectors are.
    """

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def semantic_search(
    question: str,
    db: Session,
    top_k: int = 3,
):
    """
    Find document chunks most relevant to a question.
    """

    question_vector = generate_embedding(question)

    chunks = db.scalars(
        select(DocumentChunk)
    ).all()

    results = []

    for chunk in chunks:
        chunk_vector = generate_embedding(
            chunk.content
        )

        similarity = cosine_similarity(
            question_vector,
            chunk_vector,
        )

        results.append({
            "document_id": chunk.document_id,
            "chunk_id": chunk.id,
            "content": chunk.content,
            "similarity": similarity,
        })

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return results[:top_k]