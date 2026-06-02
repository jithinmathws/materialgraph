import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.graph_job import GraphJob, JobStatus
from app.schemas.graph_job import GraphJobCreate


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