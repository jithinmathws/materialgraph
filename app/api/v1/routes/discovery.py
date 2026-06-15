from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.discovery import DiscoveryCandidatesResponse
from app.services.discovery_candidate_service import DiscoveryCandidateService

router = APIRouter(
    prefix="/materials",
    tags=["Discovery Intelligence"],
)


@router.get(
    "/{material_id}/discovery/candidates",
    response_model=DiscoveryCandidatesResponse,
)
def get_discovery_candidates(
    material_id: int,
    avoid_element: str | None = Query(default=None, min_length=1, max_length=3),
    prefer_element: str | None = Query(default=None, min_length=1, max_length=3),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    service = DiscoveryCandidateService(db)

    result = service.get_discovery_candidates(
        material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        limit=limit,
    )

    if result["mp_id"] is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result