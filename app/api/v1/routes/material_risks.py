from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_risk import MaterialRiskRead
from app.services.material_risk_service import MaterialRiskService

router = APIRouter(prefix="/material-risks", tags=["Material Risks"])


@router.get(
    "/{material_id}",
    response_model=MaterialRiskRead,
    summary="Get material risk profile",
    description=(
        "Returns the computed risk profile for a material, including "
        "element-level risk contribution and aggregate material risk."
    ),
)
def get_material_risk(
    material_id: int,
    db: Session = Depends(get_db),
):
    service = MaterialRiskService(db)
    result = service.get_material_risk(material_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result