import pytest

from app.core.database import SessionLocal


@pytest.fixture
def db_session():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()