from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas

from app.main import app
from app.core.database import Base, get_db
from pypdf import PdfWriter


@pytest.fixture
def client(tmp_path):
    # Create a temporary SQLite database
    database_path = tmp_path / "test_upload.db"

    test_engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    # Create database tables for the test
    Base.metadata.create_all(bind=test_engine)

    # Tell FastAPI to use our test database
    def override_get_db():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()


def test_upload_text_file(client):
    content = b"Floresis processes enterprise documents."

    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "test_document.txt",
                BytesIO(content),
                "text/plain",
            )
        },
        data={"department": "Operations"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["title"] == "test_document.txt"
    assert result["department"] == "Operations"
    assert result["content_type"] == "text/plain"
    assert isinstance(result["id"], int)


def test_upload_unsupported_file(client):
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "example.png",
                BytesIO(b"Not a supported image"),
                "image/png",
            )
        },
        data={"department": "Operations"},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_empty_file(client):
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "empty.txt",
                BytesIO(b""),
                "text/plain",
            )
        },
        data={"department": "Operations"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty"

def test_upload_pdf_file(client):
    pdf_buffer = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(pdf_buffer)

    pdf_buffer.seek(0)

    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "test_report.pdf",
                pdf_buffer,
                "application/pdf",
            )
        },
        data={"department": "Operations"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Uploaded file contains no extractable text"
    )

def test_upload_pdf_with_text(client):
    pdf_buffer = BytesIO()

    # Create a PDF containing real text
    pdf = canvas.Canvas(pdf_buffer)
    pdf.drawString(
        100,
        750,
        "Floresis Operations Report",
    )
    pdf.drawString(
        100,
        720,
        "Project Atlas requires weekly monitoring.",
    )
    pdf.save()

    # Return to the beginning of the PDF
    pdf_buffer.seek(0)

    # Upload the PDF to FastAPI
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "operations_report.pdf",
                pdf_buffer,
                "application/pdf",
            )
        },
        data={"department": "Operations"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["title"] == "operations_report.pdf"
    assert result["department"] == "Operations"

    # Confirm that the extracted text was stored
    chunks_response = client.get(
        f"/api/documents/{result['id']}/chunks"
    )

    assert chunks_response.status_code == 200

    chunks = chunks_response.json()["chunks"]

    assert len(chunks) > 0
    assert "Floresis Operations Report" in chunks[0]["content"]