from app.schemas.discovery import ResearchObjective
from app.services.research.objective_service import ResearchObjectiveService


def _sample_chain() -> dict:
    return {
        "hop_count": 1,
        "materials": [
            {
                "material_id": 5,
                "mp_id": "mp-19017",
                "pretty_formula": "LiFePO4",
                "formula": "LiFePO4",
            },
            {
                "material_id": 7,
                "mp_id": "mp-556540",
                "pretty_formula": "Na3Fe3(PO4)4",
                "formula": "Na3Fe3(PO4)4",
            },
        ],
        "transitions": [
            {
                "from_material_id": 5,
                "to_material_id": 7,
                "from_formula": "LiFePO4",
                "to_formula": "Na3Fe3(PO4)4",
                "transition_type": "alkali_substitution",
                "family": "phosphate",
                "reason": "Test transition.",
                "shared_elements": ["Fe", "O", "P"],
                "preserved_framework": ["Fe", "O", "P"],
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "removed_elements": ["Li"],
                "introduced_elements": ["Na"],
            }
        ],
        "chain_reason": "Test chain.",
    }


class _CapturingChainService:
    def __init__(self):
        self.calls = []

    def get_discovery_chains(self, **kwargs):
        self.calls.append(dict(kwargs))
        return {
            "material_id": kwargs["material_id"],
            "base_formula": "LiFePO4",
            "chains": [_sample_chain()],
        }


class _CapturingPathRankingService:
    def __init__(self):
        self.calls = []

    def rank_path(self, **kwargs):
        self.calls.append(dict(kwargs))
        return {
            "scientific_usefulness_score": 85.0,
            "score_breakdown": {
                "shared_element_continuity": 30.0,
                "objective_alignment": 25.0,
                "transition_plausibility": 20.0,
                "path_efficiency": 10.0,
                "material_quality": 0.0,
            },
            "usefulness_reason": "Test ranking.",
        }


def test_research_objective_chains_include_ranking_fields(db_session):
    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
        prefer_lower_criticality=True,
        require_stable_materials=False,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    assert result["material_id"] == 5
    assert result["chains"]

    for chain in result["chains"]:
        assert "scientific_usefulness_score" in chain
        assert "score_breakdown" in chain
        assert "usefulness_reason" in chain


def test_research_objective_chains_are_sorted_by_usefulness(db_session):
    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    scores = [
        chain["scientific_usefulness_score"]
        for chain in result["chains"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_research_objective_filters_preserved_elements(db_session):
    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    required = {"Fe", "P", "O"}

    for chain in result["chains"]:
        preserved = set()

        for transition in chain["transitions"]:
            preserved.update(
                transition.get("shared_elements")
                or transition["preserved_framework"]
            )

        assert required.issubset(preserved)


def test_multi_element_objective_passes_complete_sets_to_chain_generation(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service

    objective = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
        target_family=None,
        max_hops=2,
        limit=5,
    )

    service.generate_chains_for_objective(5, objective)

    call = chain_service.calls[0]
    assert set(call["avoid_elements"]) == {"Li", "Co"}
    assert set(call["prefer_elements"]) == {"Na", "K"}
    assert "avoid_element" not in call
    assert "prefer_element" not in call


def test_multi_element_objective_passes_complete_sets_to_path_ranking(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service

    objective = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
        target_family=None,
        max_hops=2,
        limit=5,
    )

    service.generate_chains_for_objective(5, objective)

    call = ranking_service.calls[0]
    assert set(call["avoid_elements"]) == {"Li", "Co"}
    assert set(call["prefer_elements"]) == {"Na", "K"}
    assert "avoid_element" not in call
    assert "prefer_element" not in call


def test_multi_element_objective_list_order_no_longer_changes_effective_sets(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service

    first = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
    )
    second = ResearchObjective(
        avoid_elements=["Co", "Li"],
        prefer_elements=["K", "Na"],
        preserve_elements=[],
    )

    service.generate_chains_for_objective(5, first)
    service.generate_chains_for_objective(5, second)

    assert set(chain_service.calls[0]["avoid_elements"]) == set(
        chain_service.calls[1]["avoid_elements"]
    )
    assert set(chain_service.calls[0]["prefer_elements"]) == set(
        chain_service.calls[1]["prefer_elements"]
    )
