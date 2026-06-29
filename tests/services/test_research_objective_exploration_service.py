from app.schemas.research_objective_exploration import (
    ResearchObjectiveExplorationRequest,
)
from app.schemas.discovery import ResearchObjective
from app.services.research_objective_exploration_service import (
    ResearchObjectiveExplorationService,
)


def test_research_objective_exploration_returns_ranked_candidates(db_session):
    service = ResearchObjectiveExplorationService(db_session)

    request = ResearchObjectiveExplorationRequest(
        objective=ResearchObjective(
            avoid_elements=["Li"],
            prefer_elements=["Na"],
            preserve_elements=["Fe", "P", "O"],
            target_family="phosphate",
            max_hops=2,
            limit=5,
        ),
        mode="balanced",
        limit=5,
    )

    result = service.explore(
        material_id=5,
        request=request,
    )

    assert result["material_id"] == 5
    assert result["mode"] == "balanced"
    assert "ranked_candidates" in result
    assert "chains" in result
    assert "warnings" in result
    assert "explanation" in result