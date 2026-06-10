from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.screening import CandidateScreeningRequest, CandidateScreeningResult
from app.services.candidate_screening_service import CandidateScreeningService

router = APIRouter(prefix="/screening", tags=["Screening"])


@router.post(
    "/candidates",
    response_model=list[CandidateScreeningResult],
    summary="Screen candidate materials",
    description=(
        "Screens candidate materials against application and risk criteria, "
        "returning ranked candidate screening results."
    ),
)
def screen_candidates(
    request: CandidateScreeningRequest,
    db: Session = Depends(get_db),
):
    service = CandidateScreeningService(db)
    return service.screen_candidates(request)