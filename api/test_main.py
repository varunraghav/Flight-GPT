import pytest
from fastapi.testclient import TestClient
from main import app
from db_utils import get_db_connection, insert_application_logs, get_chat_history
import os

client = TestClient(app)

@pytest.fixture
def setup_database():
    conn = get_db_connection()
    conn.execute("DELETE FROM application_logs")
    conn.execute("DELETE FROM document_store")
    conn.commit()
    conn.close()
    yield
    os.remove("rag_app.db")

# Test /chat endpoint
def test_chat_endpoint(setup_database):
    response = client.post("/chat", json={
        "question": "What is AI?",
        "session_id": "12345",
        "model": "gpt-4o-mini"
    })
    assert response.status_code == 200
    assert "answer" in response.json()

# Test database operations
def test_database_operations():
    insert_application_logs("123", "Hello?", "Hi there!", "gpt-4o")
    chat_history = get_chat_history("123")
    assert len(chat_history) == 2


if __name__ == "__main__":
    pytest.main(["-v", "test_main.py"])
