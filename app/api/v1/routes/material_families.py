from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_family import MaterialFamiliesResponse
from app.services.material_family_service import MaterialFamilyService

router = APIRouter(
    prefix="/materials",
    tags=["Material Families"],
)


@router.get(
    "/{material_id}/families",
    response_model=MaterialFamiliesResponse,
    summary="Get material families",
    description=(
        "Returns related materials connected by family-style relationships such as "
        "shared chemistry, alkali substitution, transition-metal similarity, "
        "phosphate framework similarity, and oxide chemistry."
    ),
)
def get_material_families(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialFamiliesResponse:
    service = MaterialFamilyService(db)

    result = service.get_material_families(material_id)

    if result["mp_id"] is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found",
        )

    return result