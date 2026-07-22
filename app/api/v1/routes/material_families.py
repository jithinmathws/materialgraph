from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_family import MaterialFamiliesResponse
from app.services.material.family_service import MaterialFamilyService

from app.api.v1.route_utils import ensure_material_found

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
        "phosphate-related elemental chemistry, and oxide chemistry."
    ),
)
def get_material_families(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialFamiliesResponse:
    service = MaterialFamilyService(db)

    result = service.get_material_families(material_id)

    ensure_material_found(result)

    return result