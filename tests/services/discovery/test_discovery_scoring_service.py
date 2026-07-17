from app.services.discovery.scoring_service import DiscoveryScoringService


def test_preferred_element_does_not_match_symbol_prefix():
    service = DiscoveryScoringService()

    score, breakdown, paths = service.apply_element_constraints(
        score=100.0,
        score_breakdown={},
        paths=set(),
        candidate_elements={"Na", "Fe", "P", "O"},
        avoid_element=None,
        prefer_element="N",
    )

    assert score == 100.0
    assert "preferred_element_bonus" not in breakdown
    assert "preferred_element" not in paths


def test_avoided_element_does_not_match_symbol_prefix():
    service = DiscoveryScoringService()

    score, breakdown, paths = service.apply_element_constraints(
        score=100.0,
        score_breakdown={},
        paths=set(),
        candidate_elements={"Na", "Fe", "P", "O"},
        avoid_element="N",
        prefer_element=None,
    )

    assert score == 125.0
    assert breakdown["avoided_element_removed_bonus"] == 25.0
    assert "avoided_element_removed" in paths
    assert "avoided_element_present_penalty" not in breakdown


def test_exact_element_membership_applies_bonus_and_penalty():
    service = DiscoveryScoringService()

    score, breakdown, paths = service.apply_element_constraints(
        score=100.0,
        score_breakdown={},
        paths=set(),
        candidate_elements={"Na", "Fe", "P", "O"},
        avoid_element="Na",
        prefer_element="Na",
    )

    assert score == 75.0
    assert breakdown["preferred_element_bonus"] == 25.0
    assert breakdown["avoided_element_present_penalty"] == -50.0
    assert "preferred_element" in paths
    assert "contains_avoided_element" in paths


def test_unknown_membership_is_not_treated_as_favorable_absence():
    service = DiscoveryScoringService()

    score, breakdown, paths = service.apply_element_constraints(
        score=100.0,
        score_breakdown={},
        paths=set(),
        candidate_elements=None,
        avoid_element="Li",
        prefer_element="Na",
    )

    assert score == 100.0
    assert breakdown == {}
    assert paths == set()


def test_source_diversity_bonus_counts_distinct_sources_only():
    service = DiscoveryScoringService()

    assert service.calculate_source_diversity_bonus(set()) == 0.0
    assert service.calculate_source_diversity_bonus({"family"}) == 0.0
    assert service.calculate_source_diversity_bonus(
        {"family", "recommendation"}
    ) == 10.0
    assert service.calculate_source_diversity_bonus(
        {"family", "recommendation", "scenario"}
    ) == 20.0


def test_set_source_diversity_bonus_replaces_existing_bonus():
    service = DiscoveryScoringService()

    breakdown = service.set_source_diversity_bonus(
        {"family_score": 100.0, "source_diversity_bonus": 10.0},
        20.0,
    )

    assert breakdown == {
        "family_score": 100.0,
        "source_diversity_bonus": 20.0,
    }
