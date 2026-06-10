from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_criticality import MaterialCriticalityResponse
from app.schemas.material_neighbor import MaterialNeighborsResponse
from app.schemas.material_neighborhood import MaterialNeighborhoodResponse
from app.schemas.material_recommendation import (
    MaterialRecommendationResponse,
    MaterialScenarioRecommendationResponse,
)
from app.schemas.material_similarity import MaterialSimilarityResponse
from app.services.material_criticality_service import MaterialCriticalityService
from app.services.material_neighbor_service import MaterialNeighborService
from app.services.material_neighborhood_service import MaterialNeighborhoodService
from app.services.material_recommendation_service import MaterialRecommendationService
from app.services.material_similarity_service import MaterialSimilarityService
from app.utils.chemical_formula import is_valid_element_symbol

from app.api.v1.route_utils import ensure_material_found

router = APIRouter(prefix="/materials", tags=["Material Intelligence"])


@router.get(
    "/{material_id}/neighbors",
    response_model=MaterialNeighborsResponse,
    summary="Get material neighbors",
    description="Returns graph-connected neighboring materials for a given material.",
)
def get_material_neighbors(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialNeighborsResponse:
    service = MaterialNeighborService(db)
    result = service.get_neighbors(material_id)

    ensure_material_found(result)

    return result


@router.get(
    "/{material_id}/similar",
    response_model=MaterialSimilarityResponse,
    summary="Get similar materials",
    description="Returns materials ranked by similarity to the selected material.",
)
def get_similar_materials(
    material_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of similar materials to return.",
    ),
    db: Session = Depends(get_db),
) -> MaterialSimilarityResponse:
    service = MaterialSimilarityService(db)
    result = service.get_similar_materials(material_id=material_id, limit=limit)

    ensure_material_found(result)

    return result


@router.get(
    "/{material_id}/neighborhood",
    response_model=MaterialNeighborhoodResponse,
    summary="Get material neighborhood",
    description=(
        "Returns a bounded material graph neighborhood around the selected material. "
        "Depth is capped to avoid expensive graph traversal."
    ),
)
def get_material_neighborhood(
    material_id: int,
    depth: int = Query(
        default=2,
        ge=1,
        le=2,
        description="Graph traversal depth. Currently capped at 2.",
    ),
    limit: int = Query(
        default=25,
        ge=1,
        le=100,
        description="Maximum number of neighborhood materials to return.",
    ),
    db: Session = Depends(get_db),
) -> MaterialNeighborhoodResponse:
    service = MaterialNeighborhoodService(db)
    result = service.get_neighborhood(
        material_id=material_id,
        depth=depth,
        limit=limit,
    )

    ensure_material_found(result)

    return result


@router.get(
    "/{material_id}/criticality",
    response_model=MaterialCriticalityResponse,
    summary="Get material criticality",
    description="Returns the computed criticality profile for a material.",
)
def get_material_criticality(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialCriticalityResponse:
    service = MaterialCriticalityService(db)
    result = service.get_material_criticality(material_id)

    ensure_material_found(result)

    return result


@router.get(
    "/{material_id}/recommendations",
    response_model=MaterialRecommendationResponse,
    summary="Get material recommendations",
    description=(
        "Returns explainable material recommendations based on similarity, "
        "criticality, shared elements, and application relevance."
    ),
)
def get_material_recommendations(
    material_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of recommendations to return.",
    ),
    prefer_lower_criticality: bool = Query(
        default=True,
        description="Whether to prioritize materials with lower criticality risk.",
    ),
    db: Session = Depends(get_db),
) -> MaterialRecommendationResponse:
    service = MaterialRecommendationService(db)

    result = service.get_recommendations(
        material_id=material_id,
        limit=limit,
        prefer_lower_criticality=prefer_lower_criticality,
    )

    ensure_material_found(result)

    return result


@router.get(
    "/{material_id}/recommendations/scenario",
    response_model=MaterialScenarioRecommendationResponse,
    summary="Get scenario-aware material recommendations",
    description=(
        "Returns explainable material recommendations adjusted by scenario constraints "
        "such as supply risk multiplier, avoided element, and preferred element."
    ),
)
def get_material_scenario_recommendations(
    material_id: int,
    element: str = Query(
        ...,
        min_length=1,
        max_length=3,
        description="Element affected by the supply risk scenario, e.g. Li.",
    ),
    supply_risk_multiplier: float = Query(
        default=1.0,
        ge=0.0,
        le=10.0,
        description="Multiplier applied to the selected element's supply risk.",
    ),
    avoid_element: str | None = Query(
        default=None,
        min_length=1,
        max_length=3,
        description="Optional element to penalize in recommendations, e.g. Co.",
    ),
    prefer_element: str | None = Query(
        default=None,
        min_length=1,
        max_length=3,
        description="Optional element to reward in recommendations, e.g. Na.",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of scenario recommendations to return.",
    ),
    db: Session = Depends(get_db),
) -> MaterialScenarioRecommendationResponse:
    if not is_valid_element_symbol(element):
        raise HTTPException(
            status_code=422,
            detail="element must be a valid chemical symbol, e.g. Li, Co, Na",
        )

    if not is_valid_element_symbol(avoid_element):
        raise HTTPException(
            status_code=422,
            detail="avoid_element must be a valid chemical symbol, e.g. Co",
        )

    if not is_valid_element_symbol(prefer_element):
        raise HTTPException(
            status_code=422,
            detail="prefer_element must be a valid chemical symbol, e.g. Na",
        )

    service = MaterialRecommendationService(db)

    result = service.get_scenario_recommendations(
        material_id=material_id,
        element=element,
        supply_risk_multiplier=supply_risk_multiplier,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        limit=limit,
    )

    ensure_material_found(result)

    return result