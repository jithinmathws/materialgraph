# app/api/v1/routes/material_neighbors.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_neighbor import MaterialNeighborsResponse
from app.schemas.material_similarity import MaterialSimilarityResponse
from app.services.material_neighbor_service import MaterialNeighborService
from app.services.material_similarity_service import MaterialSimilarityService

from app.schemas.material_neighborhood import MaterialNeighborhoodResponse
from app.services.material_neighborhood_service import MaterialNeighborhoodService

from app.schemas.material_criticality import MaterialCriticalityResponse
from app.services.material_criticality_service import MaterialCriticalityService

router = APIRouter(prefix="/materials", tags=["Material Intelligence"])


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


@router.get("/{material_id}/similar", response_model=MaterialSimilarityResponse)
def get_similar_materials(
    material_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> MaterialSimilarityResponse:
    service = MaterialSimilarityService(db)
    result = service.get_similar_materials(material_id=material_id, limit=limit)

    if result["mp_id"] is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result

@router.get("/{material_id}/neighborhood", response_model=MaterialNeighborhoodResponse)
def get_material_neighborhood(
    material_id: int,
    depth: int = Query(default=2, ge=1, le=2),
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
) -> MaterialNeighborhoodResponse:
    service = MaterialNeighborhoodService(db)
    result = service.get_neighborhood(
        material_id=material_id,
        depth=depth,
        limit=limit,
    )

    if result["mp_id"] is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result

@router.get(
    "/{material_id}/criticality",
    response_model=MaterialCriticalityResponse,
)
def get_material_criticality(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialCriticalityResponse:
    service = MaterialCriticalityService(db)

    result = service.get_material_criticality(material_id)

    if result["mp_id"] is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found",
        )

    return result