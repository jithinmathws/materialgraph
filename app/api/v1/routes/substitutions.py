from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.substitution import SubstitutionRequest, SubstitutionResult
from app.services.substitution_analysis_service import SubstitutionAnalysisService

router = APIRouter(prefix="/substitutions", tags=["Substitutions"])


@router.post("/analyze", response_model=SubstitutionResult)
def analyze_substitutions(
    request: SubstitutionRequest,
    db: Session = Depends(get_db),
):
    service = SubstitutionAnalysisService(db)
    result = service.analyze(request)

    if result is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result