from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas import DocumentCreate, QueryRequest
from app.core.config import settings
from app.core.database import Base, engine

from app.models import Document, DocumentChunk, Run
from app.services import answer, create_document_with_chunks


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

@app.get("/api/documents/{document_id}/chunks")
def get_document_chunks(document_id: int):
    with Session(engine) as session:
        document = session.get(
            Document,
            document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        chunks = session.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id
            )
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


@app.get("/api/documents")
def get_documents():

    with Session(engine) as session:

        documents = session.scalars(
            select(Document)
        ).all()

        return [
            {
                "id": document.id,
                "title": document.title,
                "department": document.department,
            }
            for document in documents
        ]


@app.post("/api/ask")
def ask_question(question_input: QueryRequest):

    with Session(engine) as session:

        documents = session.scalars(
            select(Document)
        ).all()

        generated_answer, citations = answer(
            question_input.question,
            documents,
        )

        run = Run(
            question=question_input.question,
            answer=generated_answer,
            citations=str(citations),
        )

        session.add(run)
        session.commit()

        return {
            "answer": generated_answer,
            "citations": citations,
            "grounded": bool(citations),
        }


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form("General"),
):
    try:
        content = await extract_text_from_upload(file)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    title = file.filename or "Untitled Document"

    with Session(engine) as session:
        document = create_document_with_chunks(
            session=session,
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