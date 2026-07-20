"""Tests for user registration endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud


def test_register_user_success(test_client: TestClient, test_db: Session) -> None:
    """Test successful user registration."""
    response = test_client.post("/users", json={"username": "testuser"})

    print(f"Response: {response.text}")

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data
    assert isinstance(data["id"], int)

    user = crud.get_user_by_username(test_db, "testuser")
    assert user is not None
