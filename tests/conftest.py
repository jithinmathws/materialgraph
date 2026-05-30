import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app


@pytest.fixture
def db_session():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client():
    return TestClient(app)