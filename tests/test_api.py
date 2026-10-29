
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)


def test_health():
    assert c.get("/health").json()["status"] == "ok"


def test_grounded_flow():
    fake_evidence = [
        {
            "document_id": 1,
            "chunk_id": 1,
            "content": "Project Alpha is behind schedule.",
            "similarity": 0.85,
        }
    ]

    fake_answer = {
        "answer": "Project Alpha is behind schedule.",
        "supported": True,
    }

    with patch(
        "app.services.semantic_search.semantic_search",
        return_value=fake_evidence
    ), patch(
        "app.services.llm.generate_answer",
        return_value=fake_answer
    ):
        response = c.post(
            "/api/ask",
            json={"question": "Which project is behind schedule?"}
        )

    assert response.status_code == 200

    data = response.json()

    assert data["grounded"] is True
    assert data["answer"] == "Project Alpha is behind schedule."
    assert len(data["citations"]) == 1

def test_rag_supported_question():
    fake_evidence = [
        {
            "document_id": 10,
            "chunk_id": 24,
            "content": "Complaints must be resolved within 48 hours.",
            "similarity": 0.7378,
        }
    ]

    fake_answer = {
        "answer": "Within 48 hours",
        "supported": True,
    }

    with patch(
        "app.services.semantic_search.semantic_search",
        return_value=fake_evidence
    ), patch(
        "app.services.llm.generate_answer",
        return_value=fake_answer
    ):
        response = c.post(
            "/api/ask",
            json={
                "question": "How quickly must complaints be resolved?"
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Within 48 hours"
    assert data["grounded"] is True
    assert len(data["citations"]) == 1
    assert data["citations"][0]["document_id"] == 10
    assert data["citations"][0]["chunk_id"] == 24


def test_rag_unsupported_question():
    fake_evidence = [
        {
            "document_id": 10,
            "chunk_id": 24,
            "content": "Complaints must be resolved within 48 hours.",
            "similarity": 0.4952,
        }
    ]

    fake_answer = {
        "answer": (
            "The uploaded documents do not contain enough "
            "information to answer this question."
        ),
        "supported": False,
    }

    with patch(
        "app.services.semantic_search.semantic_search",
        return_value=fake_evidence
    ), patch(
        "app.services.llm.generate_answer",
        return_value=fake_answer
    ):
        response = c.post(
            "/api/ask",
            json={
                "question": "What was the company's revenue in 2025?"
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["grounded"] is False
    assert data["citations"] == []
    assert "not contain enough information" in data["answer"]
