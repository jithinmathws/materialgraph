from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.scenario_ranking import ScenarioRankingRequest, ScenarioRankingResult
from app.services.candidate_screening_service import CandidateScreeningService
from app.services.scenario_ranking_service import ScenarioRankingService

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.post("/rank", response_model=list[ScenarioRankingResult])
def rank_scenario_candidates(
    request: ScenarioRankingRequest,
    db: Session = Depends(get_db),
):
    screening_service = CandidateScreeningService(db)
    scenario_service = ScenarioRankingService(screening_service)

    try:
        return scenario_service.rank_for_scenario(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error