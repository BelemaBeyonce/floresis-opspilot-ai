from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas import DocumentCreate, QueryRequest
from app.core.config import settings
from app.core.database import Base, engine, get_db

from app.models import Document, DocumentChunk, Run
from app.services import (
    answer,
    create_document_with_chunks,
    extract_text_from_upload,
)


# Create database tables
Base.metadata.create_all(bind=engine)


# FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Auditable enterprise knowledge and AI workflow API",
)


# Static frontend
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)




# ---------------------------------------------------------
# API endpoints
# ---------------------------------------------------------


@app.post("/api/documents")
def add_document(document_input: DocumentCreate):

    with Session(engine) as session:

        document = create_document_with_chunks(
            session=session,
            title=document_input.title,
            content=document_input.content,
            department=document_input.department,
        )

        return {
            "id": document.id,
            **document_input.model_dump(),
        }


@app.get("/api/documents/{document_id}/chunks")
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()

    return {
        "document_id": document.id,
        "title": document.title,
        "chunk_count": len(chunks),
        "chunks": [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
            }
            for chunk in chunks
        ],
    }

@app.post("/api/ask")
def ask_question(
    question_input: QueryRequest,
    db: Session = Depends(get_db),
):
    from app.services.semantic_search import semantic_search
    from app.services.llm import generate_answer

    # Retrieve the most relevant document chunks.
    evidence = semantic_search(
        question=question_input.question,
        db=db,
        top_k=1,
    )

    # Require at least some semantic similarity.
    evidence = [
        item for item in evidence
        if item["similarity"] >= 0.35
    ]

    if not evidence:
        return {
            "answer": "No relevant evidence was found in the uploaded documents.",
            "citations": [],
            "grounded": False,
        }

    result = generate_answer(
    question=question_input.question,
    evidence=evidence,
)

    if not result["supported"]:
        return {
            "answer": result["answer"],
            "citations": [],
            "grounded": False,
        }

    citations = [
        {
            "source": index,
            "document_id": item["document_id"],
            "chunk_id": item["chunk_id"],
            "similarity": round(item["similarity"], 4),
        }
        for index, item in enumerate(evidence, start=1)
    ]

    run = Run(
        question=question_input.question,
        answer=result["answer"],
        citations=str(citations),
    )

    db.add(run)
    db.commit()

    return {
        "answer": result["answer"],
        "citations": citations,
        "grounded": True,
    }


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form("General"),
    db: Session = Depends(get_db),
):
    try:
        content = await extract_text_from_upload(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    title = file.filename or "Untitled Document"

    document = create_document_with_chunks(
        session=db,
        title=title,
        content=content,
        department=department,
    )

    return {
        "id": document.id,
        "title": document.title,
        "department": document.department,
        "filename": file.filename,
        "content_type": file.content_type,
    }

# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "app/static/index.html",
        encoding="utf-8",
    ) as file:

        return file.read()

# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "opspilot",
    }