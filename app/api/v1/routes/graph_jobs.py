import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.graph_job import GraphJobCreate, GraphJobRead
from app.services.graph_job_service import GraphJobService

router = APIRouter(prefix="/graph-jobs", tags=["Graph Jobs"])


@router.post("", response_model=GraphJobRead, status_code=201)
def create_graph_job(
    payload: GraphJobCreate,
    db: Session = Depends(get_db),
) -> GraphJobRead:
    service = GraphJobService(db)
    return service.create_job(payload)


@router.get("", response_model=list[GraphJobRead])
def list_graph_jobs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[GraphJobRead]:
    service = GraphJobService(db)
    return service.list_jobs(limit=limit, offset=offset)


@router.get("/{job_id}", response_model=GraphJobRead)
def get_graph_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> GraphJobRead:
    service = GraphJobService(db)
    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Graph job not found")

    return job