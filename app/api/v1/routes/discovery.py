from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.discovery import DiscoveryCandidatesResponse, DiscoveryChainsResponse
from app.services.discovery_candidate_service import DiscoveryCandidateService
from app.services.discovery_chain_service import DiscoveryChainService
from app.schemas.discovery import (
    ResearchObjectiveChainRequest,
    ResearchObjectiveChainResponse,
)
from app.services.research_objective_service import ResearchObjectiveService
from app.schemas.discovery_graph import (
    DiscoveryGraphResponse,
    DiscoveryPathResponse,
    DiscoverySubgraphResponse,
)
from app.services.discovery_traversal_service import DiscoveryTraversalService


router = APIRouter(
    prefix="/materials",
    tags=["Discovery Intelligence"],
)


@router.get(
    "/{material_id}/discovery/candidates",
    response_model=DiscoveryCandidatesResponse,
)
def get_discovery_candidates(
    material_id: int,
    avoid_element: str | None = Query(default=None, min_length=1, max_length=3),
    prefer_element: str | None = Query(default=None, min_length=1, max_length=3),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    service = DiscoveryCandidateService(db)

    result = service.get_discovery_candidates(
        material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        limit=limit,
    )

    if result["mp_id"] is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return result

@router.get(
    "/{material_id}/discovery/chains",
    response_model=DiscoveryChainsResponse,
)
def get_discovery_chains(
    material_id: int,
    avoid_element: str | None = None,
    prefer_element: str | None = None,
    max_hops: int = Query(default=2, ge=1, le=3),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    service = DiscoveryChainService(db)

    return service.get_discovery_chains(
        material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        max_hops=max_hops,
        limit=limit,
    )

@router.post(
    "/{material_id}/discovery/objective/chains",
    response_model=ResearchObjectiveChainResponse,
)
def generate_discovery_chains_for_objective(
    material_id: int,
    request: ResearchObjectiveChainRequest,
    db: Session = Depends(get_db),
):
    service = ResearchObjectiveService(db)

    return service.generate_chains_for_objective(
        material_id=material_id,
        objective=request.objective,
    )

@router.get(
    "/materials/{material_id}/discovery/graph",
    response_model=DiscoveryGraphResponse,
)
def get_discovery_graph(
    material_id: int,
    avoid_element: str | None = None,
    prefer_element: str | None = None,
    max_hops: int = Query(2, ge=1, le=3),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = DiscoveryTraversalService(db)

    return service.get_graph(
        material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        max_hops=max_hops,
        limit=limit,
    )


@router.get(
    "/materials/{material_id}/discovery/subgraph",
    response_model=DiscoverySubgraphResponse,
)
def get_discovery_subgraph(
    material_id: int,
    avoid_element: str | None = None,
    prefer_element: str | None = None,
    family: str | None = None,
    transition_type: str | None = None,
    max_hops: int = Query(2, ge=1, le=3),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = DiscoveryTraversalService(db)

    return service.get_subgraph(
        material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        family=family,
        transition_type=transition_type,
        max_hops=max_hops,
        limit=limit,
    )


@router.get(
    "/materials/{material_id}/discovery/path",
    response_model=DiscoveryPathResponse,
)
def get_discovery_path(
    material_id: int,
    target_material_id: int = Query(...),
    avoid_element: str | None = None,
    prefer_element: str | None = None,
    max_hops: int = Query(2, ge=1, le=3),
    db: Session = Depends(get_db),
):
    service = DiscoveryTraversalService(db)

    return service.get_path(
        material_id=material_id,
        target_material_id=target_material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        max_hops=max_hops,
    )