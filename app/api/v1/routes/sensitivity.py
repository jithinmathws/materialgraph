from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sensitivity import SensitivityAnalysisRequest, SensitivityAnalysisResult
from app.services.sensitivity_analysis_service import SensitivityAnalysisService

router = APIRouter(prefix="/sensitivity", tags=["Sensitivity"])


@router.post("/material", response_model=SensitivityAnalysisResult)
def analyze_material_sensitivity(
    request: SensitivityAnalysisRequest,
    db: Session = Depends(get_db),
):
    service = SensitivityAnalysisService(db)
    result = service.analyze(request)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found under baseline screening constraints",
        )

    return result