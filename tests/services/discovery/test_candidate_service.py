from app.services.discovery.candidate_service import DiscoveryCandidateService
from app.services.discovery.explanation_service import DiscoveryExplanationService
from app.services.discovery.scoring_service import DiscoveryScoringService


def _build_service() -> DiscoveryCandidateService:
    """
    Build only the dependencies required by _upsert_candidate().

    This avoids database setup because these tests isolate candidate merge
    semantics rather than candidate retrieval.
    """
    service = DiscoveryCandidateService.__new__(DiscoveryCandidateService)
    service.scoring_service = DiscoveryScoringService()
    service.explanation_service = DiscoveryExplanationService()
    return service


def _upsert(
    service: DiscoveryCandidateService,
    candidates_by_id: dict[int, dict],
    *,
    score: float,
    score_breakdown: dict[str, float],
    paths: list[str],
    explanation: str,
    source_type: str = "family",
    substitution_path: dict | None = None,
) -> None:
    service._upsert_candidate(
        candidates_by_id=candidates_by_id,
        material_id=10,
        mp_id="mp-test-10",
        pretty_formula="NaFePO4",
        formula="NaFePO4",
        score=score,
        paths=paths,
        explanation_parts=[explanation],
        avoid_element=None,
        prefer_element=None,
        score_breakdown=score_breakdown,
        source_type=source_type,
        substitution_path=substitution_path,
        candidate_elements={"Na", "Fe", "P", "O"},
    )


def _assert_score_matches_breakdown(candidate: dict) -> None:
    assert round(sum(candidate["score_breakdown"].values()), 2) == (
        candidate["discovery_score"]
    )


def test_initial_candidate_score_matches_breakdown():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Identified through material-family relationships.",
    )

    candidate = candidates_by_id[10]

    assert candidate["discovery_score"] == 100.0
    assert candidate["score_breakdown"] == {
        "family_score": 100.0,
    }

    _assert_score_matches_breakdown(candidate)


def test_existing_aggregate_breakdown_is_retained_when_incoming_score_is_lower():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Identified through material-family relationships.",
    )

    _upsert(
        service,
        candidates_by_id,
        score=90.0,
        score_breakdown={"scenario_score": 90.0},
        paths=["scenario_recommendation"],
        source_type="scenario",
        explanation="Identified through scenario analysis.",
    )

    candidate = candidates_by_id[10]

    assert candidate["discovery_score"] == 110.0
    assert candidate["score_breakdown"] == {
        "family_score": 100.0,
        "source_diversity_bonus": 10.0,
    }

    assert "scenario_score" not in candidate["score_breakdown"]

    _assert_score_matches_breakdown(candidate)


def test_incoming_breakdown_replaces_existing_breakdown_when_incoming_score_wins():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Identified through material-family relationships.",
    )

    _upsert(
        service,
        candidates_by_id,
        score=90.0,
        score_breakdown={"recommendation_score": 90.0},
        paths=["recommendation_engine"],
        source_type="recommendation",
        explanation="Identified through recommendation analysis.",
    )

    assert candidates_by_id[10]["discovery_score"] == 110.0

    _upsert(
        service,
        candidates_by_id,
        score=115.0,
        score_breakdown={"scenario_score": 115.0},
        paths=["scenario_recommendation"],
        source_type="scenario",
        explanation="Identified through scenario analysis.",
    )

    candidate = candidates_by_id[10]

    assert candidate["discovery_score"] == 135.0
    assert candidate["score_breakdown"] == {
        "scenario_score": 115.0,
        "source_diversity_bonus": 20.0,
    }

    assert "family_score" not in candidate["score_breakdown"]
    assert "recommendation_score" not in candidate["score_breakdown"]

    _assert_score_matches_breakdown(candidate)


def test_higher_incoming_base_score_wins_even_when_existing_total_is_equal():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Identified through material-family relationships.",
    )

    _upsert(
        service,
        candidates_by_id,
        score=90.0,
        score_breakdown={"recommendation_score": 90.0},
        paths=["recommendation_engine"],
        source_type="recommendation",
        explanation="Identified through recommendation analysis.",
    )

    assert candidates_by_id[10]["discovery_score"] == 110.0
    assert candidates_by_id[10]["_base_discovery_score"] == 100.0

    _upsert(
        service,
        candidates_by_id,
        score=110.0,
        score_breakdown={"scenario_score": 110.0},
        paths=["scenario_recommendation"],
        source_type="scenario",
        explanation="Identified through scenario analysis.",
    )

    candidate = candidates_by_id[10]

    assert candidate["_base_discovery_score"] == 110.0
    assert candidate["discovery_score"] == 130.0
    assert candidate["score_breakdown"] == {
        "scenario_score": 110.0,
        "source_diversity_bonus": 20.0,
    }

    assert "family_score" not in candidate["score_breakdown"]
    assert "recommendation_score" not in candidate["score_breakdown"]

    _assert_score_matches_breakdown(candidate)


def test_exact_base_score_tie_retains_existing_breakdown():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Identified through material-family relationships.",
    )

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"recommendation_score": 100.0},
        paths=["recommendation_engine"],
        source_type="recommendation",
        explanation="Identified through recommendation analysis.",
    )

    candidate = candidates_by_id[10]

    assert candidate["_base_discovery_score"] == 100.0
    assert candidate["discovery_score"] == 110.0
    assert candidate["score_breakdown"] == {
        "family_score": 100.0,
        "source_diversity_bonus": 10.0,
    }

    assert "recommendation_score" not in candidate["score_breakdown"]

    _assert_score_matches_breakdown(candidate)


def test_incoming_base_score_is_compared_without_existing_diversity_bonus():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Family candidate.",
        source_type="family",
    )

    _upsert(
        service,
        candidates_by_id,
        score=90.0,
        score_breakdown={"recommendation_score": 90.0},
        paths=["recommendation_engine"],
        explanation="Recommendation candidate.",
        source_type="recommendation",
    )

    assert candidates_by_id[10]["discovery_score"] == 110.0

    _upsert(
        service,
        candidates_by_id,
        score=105.0,
        score_breakdown={"scenario_score": 105.0},
        paths=["scenario_recommendation"],
        explanation="Scenario candidate.",
        source_type="scenario",
    )

    candidate = candidates_by_id[10]

    assert candidate["_base_discovery_score"] == 105.0
    assert candidate["discovery_score"] == 125.0
    assert candidate["score_breakdown"] == {
        "scenario_score": 105.0,
        "source_diversity_bonus": 20.0,
    }

    _assert_score_matches_breakdown(candidate)


def test_losing_source_still_contributes_contextual_paths_and_explanations():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"family_score": 100.0},
        paths=["family_related"],
        explanation="Identified through material-family relationships.",
    )

    _upsert(
        service,
        candidates_by_id,
        score=90.0,
        score_breakdown={"scenario_score": 90.0},
        paths=["scenario_recommendation"],
        source_type="scenario",
        explanation="Identified through scenario analysis.",
    )

    candidate = candidates_by_id[10]

    assert "family_related" in candidate["discovery_path"]
    assert "scenario_recommendation" in candidate["discovery_path"]

    assert (
        "Identified through material-family relationships."
        in candidate["explanation"]
    )
    assert "Identified through scenario analysis." in candidate["explanation"]

    _assert_score_matches_breakdown(candidate)


def test_later_encounter_can_populate_missing_substitution_path():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(
        service,
        candidates_by_id,
        score=100.0,
        score_breakdown={"recommendation_score": 100.0},
        paths=["recommendation_engine"],
        source_type="recommendation",
        explanation="Identified through recommendation analysis.",
        substitution_path=None,
    )

    substitution_path = {
        "path_type": "alkali_substitution",
        "from_formula": "LiFePO4",
        "to_formula": "NaFePO4",
        "replaced_elements": ["Li"],
        "introduced_elements": ["Na"],
        "shared_elements": ["Fe", "O", "P"],
        "preserved_framework": ["Fe", "O", "P"],
        "preservation_basis": "element_overlap",
        "structural_preservation_validated": False,
        "reason": (
            "The materials share Fe, O, and P elements; structural "
            "preservation is not validated."
        ),
    }

    _upsert(
        service,
        candidates_by_id,
        score=90.0,
        score_breakdown={"family_score": 90.0},
        paths=["family_related", "alkali_substitution"],
        explanation="Identified through material-family relationships.",
        substitution_path=substitution_path,
    )

    candidate = candidates_by_id[10]

    assert candidate["substitution_path"] == substitution_path

    _assert_score_matches_breakdown(candidate)

def test_repeated_encounter_from_same_source_does_not_add_diversity_bonus():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(service, candidates_by_id, score=100.0,
            score_breakdown={"family_score": 100.0},
            paths=["family_related"], explanation="First family.",
            source_type="family")
    _upsert(service, candidates_by_id, score=90.0,
            score_breakdown={"family_score": 90.0},
            paths=["shared_chemistry"], explanation="Second family.",
            source_type="family")

    candidate = candidates_by_id[10]
    assert candidate["discovery_score"] == 100.0
    assert candidate["score_breakdown"] == {"family_score": 100.0}
    assert candidate["_source_types"] == {"family"}
    _assert_score_matches_breakdown(candidate)


def test_distinct_sources_add_bonus_once_per_additional_source():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(service, candidates_by_id, score=100.0,
            score_breakdown={"family_score": 100.0},
            paths=["family_related"], explanation="Family.",
            source_type="family")
    _upsert(service, candidates_by_id, score=90.0,
            score_breakdown={"recommendation_score": 90.0},
            paths=["recommendation_engine"], explanation="Recommendation.",
            source_type="recommendation")
    _upsert(service, candidates_by_id, score=80.0,
            score_breakdown={"scenario_score": 80.0},
            paths=["scenario_recommendation"], explanation="Scenario.",
            source_type="scenario")

    candidate = candidates_by_id[10]
    assert candidate["discovery_score"] == 120.0
    assert candidate["score_breakdown"] == {
        "family_score": 100.0,
        "source_diversity_bonus": 20.0,
    }
    assert candidate["_source_types"] == {"family", "recommendation", "scenario"}
    _assert_score_matches_breakdown(candidate)


def test_repeated_existing_source_does_not_increase_diversity_bonus():
    service = _build_service()
    candidates_by_id: dict[int, dict] = {}

    _upsert(service, candidates_by_id, score=100.0,
            score_breakdown={"family_score": 100.0},
            paths=["family_related"], explanation="Family.",
            source_type="family")
    _upsert(service, candidates_by_id, score=90.0,
            score_breakdown={"recommendation_score": 90.0},
            paths=["recommendation_engine"], explanation="Recommendation.",
            source_type="recommendation")
    _upsert(service, candidates_by_id, score=85.0,
            score_breakdown={"recommendation_score": 85.0},
            paths=["similar_material"], explanation="Recommendation again.",
            source_type="recommendation")

    candidate = candidates_by_id[10]
    assert candidate["discovery_score"] == 110.0
    assert candidate["score_breakdown"] == {
        "family_score": 100.0,
        "source_diversity_bonus": 10.0,
    }
    assert candidate["_source_types"] == {"family", "recommendation"}
    _assert_score_matches_breakdown(candidate)