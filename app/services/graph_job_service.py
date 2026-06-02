import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.graph_job import GraphJob, JobStatus
from app.schemas.graph_job import GraphJobCreate

def utc_now() -> datetime:
    return datetime.now(UTC)

class GraphJobService:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, payload: GraphJobCreate) -> GraphJob:
        job = GraphJob(
            job_type=payload.job_type,
            status=JobStatus.PENDING,
            input_json=payload.input_json,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_job(self, job_id: uuid.UUID) -> GraphJob | None:
        return self.db.get(GraphJob, job_id)

    def list_jobs(self, limit: int = 50, offset: int = 0) -> list[GraphJob]:
        stmt = (
            select(GraphJob)
            .order_by(GraphJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(self.db.scalars(stmt).all())

    def claim_next_pending_job(self) -> GraphJob | None:
        stmt = (
            select(GraphJob)
            .where(GraphJob.status == JobStatus.PENDING)
            .order_by(GraphJob.created_at.asc())
            .limit(1)
        )

        job = self.db.scalars(stmt).first()

        if job is None:
            return None

        job.status = JobStatus.RUNNING
        job.started_at = utc_now()
        job.updated_at = utc_now()

        self.db.commit()
        self.db.refresh(job)

        return job


    def complete_job(self, job_id: uuid.UUID, result_json: dict) -> GraphJob | None:
        job = self.get_job(job_id)

        if job is None:
            return None

        job.status = JobStatus.COMPLETED
        job.result_json = result_json
        job.completed_at = utc_now()
        job.updated_at = utc_now()

        self.db.commit()
        self.db.refresh(job)

        return job


    def fail_job(self, job_id: uuid.UUID, error_message: str) -> GraphJob | None:
        job = self.get_job(job_id)

        if job is None:
            return None

        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.completed_at = utc_now()
        job.updated_at = utc_now()

        self.db.commit()
        self.db.refresh(job)

        return job