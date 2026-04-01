"""Smoke tests for the RAG FastAPI application."""

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health_endpoint():
    """Health check should return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_rejects_empty_question():
    """Query endpoint should reject an empty question with 400."""
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_query_rejects_missing_body():
    """Query endpoint should reject a request with no body."""
    response = client.post("/query")
    assert response.status_code == 422


def test_ingest_rejects_non_pdf():
    """Ingest endpoint should reject non-PDF files."""
    response = client.post(
        "/ingest",
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]
