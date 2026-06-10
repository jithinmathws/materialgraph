from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.element_risk_profile import ElementRiskProfile
from app.schemas.risk import ElementRiskProfileRead

router = APIRouter(prefix="/risks", tags=["Risks"])


@router.get(
    "/elements",
    response_model=list[ElementRiskProfileRead],
    summary="List element risk profiles",
    description="Returns element-level risk profiles ordered by latest year first.",
)
def list_element_risk_profiles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(ElementRiskProfile)
        .order_by(ElementRiskProfile.year.desc(), ElementRiskProfile.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/elements/{risk_profile_id}", response_model=ElementRiskProfileRead)
def get_element_risk_profile(risk_profile_id: int, db: Session = Depends(get_db)):
    risk_profile = (
        db.query(ElementRiskProfile)
        .filter(ElementRiskProfile.id == risk_profile_id)
        .first()
    )

    if risk_profile is None:
        raise HTTPException(status_code=404, detail="Element risk profile not found")

    return risk_profile