from app.schemas.discovery import ResearchObjective
from app.schemas.research_objective_exploration import (
    ResearchObjectiveExplorationRequest,
)
from app.services.research.objective_exploration_service import (
    ResearchObjectiveExplorationService,
)


class _ObjectiveServiceStub:
    def __init__(self, chains: list[dict]):
        self.chains = chains

    def generate_chains_for_objective(self, material_id: int, objective) -> dict:
        return {
            "material_id": material_id,
            "base_formula": "LiFePO4",
            "objective": objective,
            "chains": self.chains,
        }


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


def test_multi_element_exploration_candidate_scoring_uses_all_preferred_elements(
    db_session,
):
    """Characterize the later full-list semantics in objective exploration."""

    service = ResearchObjectiveExplorationService(db_session)

    objective = ResearchObjective(
        avoid_elements=[],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
        target_family=None,
        max_hops=1,
        limit=5,
    )

    score = service._score_material(
        material={
            "material_id": 101,
            "formula": "NaKFePO4",
            "pretty_formula": "NaKFePO4",
        },
        transitions=[],
        objective=objective,
        mode="balanced",
    )

    assert score == 80.0


def test_multi_element_exploration_candidate_scoring_uses_all_avoided_elements(
    db_session,
):
    """Characterize that all avoid elements are applied after chain generation."""

    service = ResearchObjectiveExplorationService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=[],
        preserve_elements=[],
        target_family=None,
        max_hops=1,
        limit=5,
    )

    score = service._score_material(
        material={
            "material_id": 102,
            "formula": "LiCoO2",
            "pretty_formula": "LiCoO2",
        },
        transitions=[],
        objective=objective,
        mode="balanced",
    )

    assert score == 0.0


def test_exploration_cannot_recover_candidate_missing_from_generated_chains(
    db_session,
):
    """Characterize the irreversible scalar-generated opportunity boundary."""

    service = ResearchObjectiveExplorationService(db_session)
    service.objective_service = _ObjectiveServiceStub(
        chains=[
            {
                "hop_count": 1,
                "materials": [
                    {
                        "material_id": 5,
                        "formula": "LiFePO4",
                        "pretty_formula": "LiFePO4",
                    },
                    {
                        "material_id": 7,
                        "formula": "Na3Fe3(PO4)4",
                        "pretty_formula": "Na3Fe3(PO4)4",
                    },
                ],
                "transitions": [],
                "chain_reason": "Stub chain.",
                "scientific_usefulness_score": 0.0,
                "score_breakdown": {},
                "usefulness_reason": "Stub ranking.",
            }
        ]
    )

    request = ResearchObjectiveExplorationRequest(
        objective=ResearchObjective(
            avoid_elements=[],
            prefer_elements=["Na", "K"],
            preserve_elements=[],
            target_family=None,
            max_hops=1,
            limit=5,
        ),
        mode="balanced",
        limit=5,
    )

    result = service.explore(
        material_id=5,
        request=request,
    )

    returned_ids = {
        candidate["material_id"]
        for candidate in result["ranked_candidates"]
    }

    assert returned_ids == {7}
    assert 999 not in returned_ids
