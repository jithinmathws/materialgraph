import pytest

from app.schemas.scenario_ranking import ScenarioRankingRequest
from app.services.candidate_screening_service import CandidateScreeningService
from app.services.scenario_ranking_service import ScenarioRankingService


def test_lithium_supply_shock_ranking_returns_top_candidates(db_session):
    screening_service = CandidateScreeningService(db_session)
    service = ScenarioRankingService(screening_service)

    result = service.rank_for_scenario(
        ScenarioRankingRequest(
            scenario_name="lithium_supply_shock",
            top_n=5,
        )
    )

    assert len(result) <= 5
    assert len(result) > 0
    assert result[0].rank == 1
    assert result[0].scenario_name == "lithium_supply_shock"
    assert result[0].score >= 0


def test_unknown_scenario_raises_error(db_session):
    screening_service = CandidateScreeningService(db_session)
    service = ScenarioRankingService(screening_service)

    with pytest.raises(ValueError):
        service.rank_for_scenario(
            ScenarioRankingRequest(
                scenario_name="unknown_scenario",
                top_n=5,
            )
        )