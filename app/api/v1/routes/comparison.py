from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.comparison import CandidateComparisonRequest, CandidateComparisonResult
from app.services.candidate_comparison_service import CandidateComparisonService

router = APIRouter(prefix="/comparison", tags=["Comparison"])


@router.post(
    "/materials",
    response_model=CandidateComparisonResult,
    summary="Compare candidate materials",
    description=(
        "Compares two candidate materials under selected constraints, "
        "including similarity, risk, and recommendation-relevant signals."
    ),
)
def compare_materials(
    request: CandidateComparisonRequest,
    db: Session = Depends(get_db),
):
    service = CandidateComparisonService(db)
    result = service.compare_candidates(request)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="One or both materials were not found under the selected constraints",
        )

    return result