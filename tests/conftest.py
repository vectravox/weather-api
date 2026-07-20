"""Pytest fixtures for Weather API tests."""

import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def test_db() -> Generator[Session]:
    """Create test database in memory."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        os.unlink(db_path)


@pytest.fixture
def test_client(test_db: Session) -> Generator[TestClient]:
    """Create test client with database override."""

    def get_test_db() -> Session:
        return test_db

    app.dependency_overrides[get_db] = get_test_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
