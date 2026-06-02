from app.models.graph_job import JobStatus
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