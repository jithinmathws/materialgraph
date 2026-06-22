from app.services.discovery_path_ranking_service import DiscoveryPathRankingService


def test_rank_path_scores_full_alkali_substitution_path():
    service = DiscoveryPathRankingService()

    transitions = [
        {
            "transition_type": "alkali_substitution",
            "family": "phosphate",
            "preserved_framework": ["Fe", "O", "P"],
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
        }
    ]

    result = service.rank_path(
        materials=[],
        transitions=transitions,
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["scientific_usefulness_score"] == 100.0
    assert result["score_breakdown"]["framework_preservation"] == 35.0
    assert result["score_breakdown"]["objective_alignment"] == 30.0
    assert result["score_breakdown"]["transition_plausibility"] == 25.0
    assert result["score_breakdown"]["path_efficiency"] == 10.0
    assert "removes avoided element Li" in result["usefulness_reason"]
    assert "introduces preferred element Na" in result["usefulness_reason"]


def test_rank_path_scores_two_hop_path_efficiency_lower():
    service = DiscoveryPathRankingService()

    transitions = [
        {
            "transition_type": "alkali_substitution",
            "family": "phosphate",
            "preserved_framework": ["Fe", "O", "P"],
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
        },
        {
            "transition_type": "family_expansion",
            "family": "phosphate",
            "preserved_framework": ["Fe", "Na", "O", "P"],
            "removed_elements": [],
            "introduced_elements": [],
        },
    ]

    result = service.rank_path(
        materials=[],
        transitions=transitions,
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["scientific_usefulness_score"] == 95.62
    assert result["score_breakdown"]["framework_preservation"] == 35.0
    assert result["score_breakdown"]["objective_alignment"] == 30.0
    assert result["score_breakdown"]["transition_plausibility"] == 23.12
    assert result["score_breakdown"]["path_efficiency"] == 7.5


def test_rank_path_handles_empty_path():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[],
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["scientific_usefulness_score"] == 0.0
    assert result["score_breakdown"]["framework_preservation"] == 0.0
    assert result["score_breakdown"]["objective_alignment"] == 0.0
    assert result["score_breakdown"]["transition_plausibility"] == 0.0
    assert result["score_breakdown"]["path_efficiency"] == 0.0
    assert result["usefulness_reason"] == "No discovery path was available for ranking."