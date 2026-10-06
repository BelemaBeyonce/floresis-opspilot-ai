from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas import DocumentCreate, QueryRequest
from app.core.config import settings
from app.core.database import Base, engine
from app.models import Document, Run
from app.services import answer


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

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "opspilot",
    }


@app.post("/api/documents")
def add_document(document_input: DocumentCreate):

    with Session(engine) as session:

        document = Document(
            **document_input.model_dump()
        )

        session.add(document)
        session.commit()
        session.refresh(document)

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


@app.post("/api/seed")
def seed_demo_data():

    samples = [
        (
            "Q3 Delivery Review",
            (
                "Project Atlas is 18 days behind schedule because "
                "vendor integration testing started late. "
                "Management review is required before the next release gate."
            ),
            "PMO",
        ),
        (
            "AI Governance Policy",
            (
                "High-risk AI workflows require human approval, "
                "source citations, audit logs, and quarterly evaluation "
                "for accuracy and harmful outputs."
            ),
            "Risk",
        ),
        (
            "Support Operations",
            (
                "Priority-one incidents require acknowledgement "
                "within 15 minutes and an incident review within "
                "two business days."
            ),
            "Operations",
        ),
    ]

    with Session(engine) as session:

        existing_document = session.scalar(
            select(Document.id).limit(1)
        )

        if not existing_document:

            session.add_all(
                [
                    Document(
                        title=title,
                        content=content,
                        department=department,
                    )
                    for title, content, department in samples
                ]
            )

            session.commit()

    return {
        "seeded": True,
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