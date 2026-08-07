from uuid import uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.graph_job import GraphJob, JobStatus
from app.schemas.graph_job import GraphJobCreate
from app.services.graph_job_service import GraphJobService


def test_create_job(db_session):
    service = GraphJobService(db_session)

    job = service.create_job(
        GraphJobCreate(
            job_type="SIMILARITY_SEARCH",
            input_json={"material_id": 1},
        )
    )

    assert job.id is not None
    assert job.job_type == "SIMILARITY_SEARCH"
    assert job.status == JobStatus.PENDING
    assert job.input_json == {"material_id": 1}


def test_claim_next_pending_job(db_session):
    service = GraphJobService(db_session)

    service.create_job(
        GraphJobCreate(
            job_type="SIMILARITY_SEARCH",
            input_json={"material_id": 1},
        )
    )

    claimed = service.claim_next_pending_job()

    assert claimed is not None
    assert claimed.status == JobStatus.RUNNING
    assert claimed.started_at is not None


def test_complete_job(db_session):
    service = GraphJobService(db_session)

    job = service.create_job(
        GraphJobCreate(
            job_type="SIMILARITY_SEARCH",
            input_json={"material_id": 1},
        )
    )

    completed = service.complete_job(
        job_id=job.id,
        result_json={"neighbors": [1, 2, 3]},
    )

    assert completed is not None
    assert completed.status == JobStatus.COMPLETED
    assert completed.result_json == {"neighbors": [1, 2, 3]}
    assert completed.completed_at is not None


def test_fail_job(db_session):
    service = GraphJobService(db_session)

    job = service.create_job(
        GraphJobCreate(
            job_type="SIMILARITY_SEARCH",
            input_json={"material_id": 1},
        )
    )

    failed = service.fail_job(
        job_id=job.id,
        error_message="Computation failed",
    )

    assert failed is not None
    assert failed.status == JobStatus.FAILED
    assert failed.error_message == "Computation failed"
    assert failed.completed_at is not None


def test_claim_returns_none_when_no_pending_job_exists(db_session):
    service = GraphJobService(db_session)

    claimed = service.claim_next_pending_job()

    assert claimed is None


def test_claim_does_not_select_running_job(db_session):
    service = GraphJobService(db_session)

    first_claim = service.create_job(
        GraphJobCreate(
            job_type="SIMILARITY_SEARCH",
            input_json={"material_id": 1},
        )
    )
    claimed = service.claim_next_pending_job()

    assert claimed is not None
    assert claimed.id == first_claim.id
    assert claimed.status == JobStatus.RUNNING

    second_claim = service.claim_next_pending_job()

    assert second_claim is None


def test_claims_pending_jobs_in_creation_order(db_session):
    service = GraphJobService(db_session)

    first = service.create_job(
        GraphJobCreate(
            job_type="FIRST",
            input_json={"material_id": 1},
        )
    )
    second = service.create_job(
        GraphJobCreate(
            job_type="SECOND",
            input_json={"material_id": 2},
        )
    )

    first_claim = service.claim_next_pending_job()
    second_claim = service.claim_next_pending_job()

    assert first_claim is not None
    assert second_claim is not None
    assert first_claim.id == first.id
    assert second_claim.id == second.id


def test_claim_skips_job_locked_by_another_session():
    if engine.dialect.name != "postgresql":
        pytest.skip("SKIP LOCKED behavior requires PostgreSQL")

    marker = uuid4().hex
    setup_session = Session(bind=engine)
    locking_session = Session(bind=engine)
    claiming_session = Session(bind=engine)
    created_ids = []

    try:
        setup_service = GraphJobService(setup_session)

        first = setup_service.create_job(
            GraphJobCreate(
                job_type=f"TEST_FIRST_{marker}",
                input_json={"test_marker": marker},
            )
        )
        second = setup_service.create_job(
            GraphJobCreate(
                job_type=f"TEST_SECOND_{marker}",
                input_json={"test_marker": marker},
            )
        )
        created_ids = [first.id, second.id]

        locking_session.scalars(
            select(GraphJob)
            .where(GraphJob.id == first.id)
            .with_for_update()
        ).one()

        claimed = GraphJobService(
            claiming_session
        ).claim_next_pending_job()

        assert claimed is not None
        assert claimed.id == second.id
        assert claimed.status == JobStatus.RUNNING
    finally:
        locking_session.rollback()
        claiming_session.rollback()

        locking_session.close()
        claiming_session.close()
        setup_session.close()

        if created_ids:
            with Session(bind=engine) as cleanup_session:
                cleanup_session.execute(
                    delete(GraphJob).where(GraphJob.id.in_(created_ids))
                )
                cleanup_session.commit()


def test_claim_returns_none_when_only_pending_job_is_locked():
    if engine.dialect.name != "postgresql":
        pytest.skip("SKIP LOCKED behavior requires PostgreSQL")

    marker = uuid4().hex
    setup_session = Session(bind=engine)
    locking_session = Session(bind=engine)
    claiming_session = Session(bind=engine)

    try:
        job = GraphJobService(setup_session).create_job(
            GraphJobCreate(
                job_type=f"TEST_ONLY_{marker}",
                input_json={"test_marker": marker},
            )
        )

        locked_job = locking_session.scalars(
            select(GraphJob)
            .where(GraphJob.id == job.id)
            .with_for_update()
        ).one()

        assert locked_job.status == JobStatus.PENDING

        claimed = GraphJobService(
            claiming_session
        ).claim_next_pending_job()

        assert claimed is None
    finally:
        locking_session.rollback()
        claiming_session.rollback()
        setup_session.rollback()

        locking_session.close()
        claiming_session.close()
        setup_session.close()