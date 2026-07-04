from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.discovery import DiscoveryCandidatesResponse, DiscoveryChainsResponse
from app.services.discovery.candidate_service import DiscoveryCandidateService
from app.services.discovery.chain_service import DiscoveryChainService
from app.schemas.discovery import (
    ResearchObjectiveChainRequest,
    ResearchObjectiveChainResponse,
)

from app.schemas.discovery_graph import (
    DiscoveryGraphResponse,
    DiscoveryPathResponse,
    DiscoverySubgraphResponse,
)
from app.services.discovery.traversal_service import DiscoveryTraversalService
from app.services.discovery.graph_analytics_service import (
    DiscoveryGraphAnalyticsService,
)
from app.schemas.research_objective_exploration import (
    ResearchObjectiveExplorationRequest,
    ResearchObjectiveExplorationResponse,
)
from app.services.research.objective_exploration_service import (
    ResearchObjectiveService,
    ResearchObjectiveExplorationService,
)



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
    "/{material_id}/discovery/graph",
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
    "/{material_id}/discovery/subgraph",
    response_model=DiscoverySubgraphResponse,
)
def get_discovery_subgraph(
    material_id: int,
    avoid_element: str | None = Query(default=None, min_length=1, max_length=3),
    prefer_element: str | None = Query(default=None, min_length=1, max_length=3),
    family: str | None = Query(default=None),
    transition_type: str | None = Query(default=None),
    min_quality_score: float | None = Query(default=None, ge=0.0, le=15.0),
    min_edge_score: float | None = Query(default=None, ge=0.0, le=100.0),
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
        min_quality_score=min_quality_score,
        min_edge_score=min_edge_score,
        max_hops=max_hops,
        limit=limit,
    )


@router.get(
    "/{material_id}/discovery/path",
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

@router.get(
    "/{material_id}/discovery/communities/connected",
    summary="Get connected discovery communities",
)
def get_connected_discovery_communities(
    material_id: int,
    avoid_element: str | None = Query(default=None, min_length=1, max_length=3),
    prefer_element: str | None = Query(default=None, min_length=1, max_length=3),
    max_depth: int = Query(default=2, ge=1, le=2),
    db: Session = Depends(get_db),
):
    service = DiscoveryGraphAnalyticsService(db)

    return service.connected_components(
        start_material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        max_depth=max_depth,
    )


@router.get(
    "/{material_id}/discovery/communities/modularity",
    summary="Get modularity-based discovery communities",
)
def get_modularity_discovery_communities(
    material_id: int,
    avoid_element: str | None = Query(default=None, min_length=1, max_length=3),
    prefer_element: str | None = Query(default=None, min_length=1, max_length=3),
    max_depth: int = Query(default=2, ge=1, le=2),
    db: Session = Depends(get_db),
):
    service = DiscoveryGraphAnalyticsService(db)

    return service.greedy_modularity_communities(
        start_material_id=material_id,
        avoid_element=avoid_element,
        prefer_element=prefer_element,
        max_depth=max_depth,
    )

@router.post(
    "/{material_id}/discovery/objective/explore",
    response_model=ResearchObjectiveExplorationResponse,
    summary="Explore a research objective",
)
def explore_research_objective(
    material_id: int,
    request: ResearchObjectiveExplorationRequest,
    db: Session = Depends(get_db),
):
    service = ResearchObjectiveExplorationService(db)

    return service.explore(
        material_id=material_id,
        request=request,
    )