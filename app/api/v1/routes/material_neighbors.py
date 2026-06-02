from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_neighbor import MaterialNeighborsResponse
from app.services.material_neighbor_service import MaterialNeighborService

router = APIRouter(prefix="/materials", tags=["Material Neighbors"])


@router.get("/{material_id}/neighbors", response_model=MaterialNeighborsResponse)
def get_material_neighbors(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialNeighborsResponse:
    service = MaterialNeighborService(db)
    result = service.get_neighbors(material_id)

    if result["mp_id"] is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result