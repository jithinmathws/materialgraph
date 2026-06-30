from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.discovery import ResearchObjectiveChainRequest
from app.services.research.scientific_pathway_analysis_service import (
    ScientificPathwayAnalysisService,
)
from app.schemas.research_objective_exploration import (
    ScientificPathwayAnalysisResponse,
)

router = APIRouter(
    prefix="/materials",
    tags=["Research Intelligence"],
)


@router.post(
    "/{material_id}/research/scientific-pathways",
    response_model=ScientificPathwayAnalysisResponse,
    summary="Analyze scientific pathway opportunities",
)
def analyze_scientific_pathways(
    material_id: int,
    request: ResearchObjectiveChainRequest,
    db: Session = Depends(get_db),
):
    service = ScientificPathwayAnalysisService(db)

    return service.analyze(
        material_id=material_id,
        objective=request.objective,
    )