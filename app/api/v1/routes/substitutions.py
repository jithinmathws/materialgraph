from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.substitution import SubstitutionRequest, SubstitutionResult
from app.services.substitution_analysis_service import SubstitutionAnalysisService

router = APIRouter(prefix="/substitutions", tags=["Substitutions"])


@router.post(
    "/analyze",
    response_model=SubstitutionResult,
    summary="Analyze material substitutions",
    description=(
        "Analyzes possible material substitutions and returns candidate "
        "alternatives with risk and similarity context."
    ),
)
def analyze_substitutions(
    request: SubstitutionRequest,
    db: Session = Depends(get_db),
):
    service = SubstitutionAnalysisService(db)
    result = service.analyze(request)

    if result is None:
        raise HTTPException(status_code=404, detail="Material substitution analysis target not found")

    return result