"""Tests for user registration endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import config, crud


def test_register_user_success(test_client: TestClient, test_db: Session) -> None:
    """Test successful user registration."""
    response = test_client.post("/users", json={"username": "testuser"})

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data
    assert isinstance(data["id"], int)

    user = crud.get_user_by_username(test_db, "testuser")
    assert user is not None
    assert user.username == "testuser"


def test_register_user_duplicate_username(test_client: TestClient) -> None:
    """Test registration with duplicate username returns 409."""
    test_client.post("/users", json={"username": "testuser"})
    response = test_client.post("/users", json={"username": "testuser"})

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]

# NOTE: Update app/config.py if you change these test values
@pytest.mark.parametrize(
    "username",
    [
        "a" * (config.USERNAME_MIN_LENGTH - 1),
        "a" * (config.USERNAME_MAX_LENGTH + 1),
        "",
        "test@user",
        "test user",
        "test-user",
        "test.user",
        "test_user!",
        "Тест",
        "user@name",
    ],
)
def test_register_user_invalid_usernames(
    test_client: TestClient, username: str
) -> None:
    """Test registration with invalid usernames."""
    response = test_client.post("/users", json={"username": username})
    assert response.status_code == 422


# NOTE: Update app/config.py if you change these test values
@pytest.mark.parametrize(
    "username",
    [
        "a" * config.USERNAME_MIN_LENGTH,
        "a" * config.USERNAME_MAX_LENGTH,
        "_Valid_User_123_",
    ],
)
def test_register_user_valid_usernames(test_client: TestClient, username: str) -> None:
    """Test registration with valid usernames."""
    response = test_client.post("/users", json={"username": username})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
