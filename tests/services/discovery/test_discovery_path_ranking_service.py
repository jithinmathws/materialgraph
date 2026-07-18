from app.services.discovery.path_ranking_service import (
    DiscoveryPathRankingService,
)


def _transition(
    removed=None,
    introduced=None,
):
    return {
        "transition_type": "alkali_substitution",
        "family": "phosphate",
        "shared_elements": ["Fe", "O", "P"],
        "preserved_framework": ["Fe", "O", "P"],
        "removed_elements": removed or [],
        "introduced_elements": introduced or [],
    }


def test_rank_path_scores_full_alkali_substitution_path():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["scientific_usefulness_score"] == 85.0
    assert result["score_breakdown"]["objective_alignment"] == 25.0


def test_multi_element_objective_alignment_is_proportional_and_capped():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 12.5
    assert result["score_breakdown"]["objective_alignment"] <= 25.0


def test_multi_element_objective_full_event_alignment_keeps_existing_maximum():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[
            _transition(
                ["Li", "Co"],
                ["Na", "K"],
            )
        ],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 25.0


def test_multi_element_objective_alignment_is_order_independent():
    service = DiscoveryPathRankingService()
    transitions = [_transition(["Li"], ["Na"])]

    first = service.rank_path(
        materials=[],
        transitions=transitions,
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )
    second = service.rank_path(
        materials=[],
        transitions=transitions,
        avoid_elements=["Co", "Li"],
        prefer_elements=["K", "Na"],
    )

    assert (
        first["score_breakdown"]["objective_alignment"]
        == second["score_breakdown"]["objective_alignment"]
    )


def test_multi_element_reason_reports_matched_and_unmatched_events():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    reason = result["usefulness_reason"]
    assert "Li" in reason
    assert "Co" in reason
    assert "Na" in reason
    assert "K" in reason


def test_rank_path_handles_empty_path():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result["scientific_usefulness_score"] == 0.0
    assert result["usefulness_reason"] == (
        "No discovery path was available for ranking."
    )
