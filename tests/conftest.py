import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.database import engine
from app.main import app
from app.models.graph_job import GraphJob


def _assert_test_database() -> None:
    database_name = engine.url.database or ""

    if "test" not in database_name.lower():
        raise RuntimeError(
            f"Refusing to clean graph jobs in non-test database: {database_name}"
        )


@pytest.fixture(autouse=True)
def clean_graph_jobs():
    _assert_test_database()

    with engine.begin() as connection:
        connection.execute(delete(GraphJob))

    yield

    with engine.begin() as connection:
        connection.execute(delete(GraphJob))


@pytest.fixture
def db_session():
    connection = engine.connect()
    outer_transaction = connection.begin()

    db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield db
    finally:
        db.close()

        if outer_transaction.is_active:
            outer_transaction.rollback()

        connection.close()


@pytest.fixture
def client():
    return TestClient(app)