from app.services.discovery.path_ranking_service import DiscoveryPathRankingService

def test_path_ranking_preserves_scores_but_qualifies_reason():
    result = DiscoveryPathRankingService().rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
        ],
        transitions=[
            {
                "transition_type": "alkali_substitution",
                "family": "phosphate",
                "shared_elements": ["Fe", "O", "P"],
                "preserved_framework": ["Fe", "O", "P"],
                "removed_elements": ["Li"],
                "introduced_elements": ["Na"],
            }
        ],
        avoid_element="Li",
        prefer_element="Na",
    )
    assert result["scientific_usefulness_score"]==85.0
    breakdown = result["score_breakdown"]

    assert breakdown["shared_element_continuity"] == 30.0
    assert "framework_preservation" not in breakdown
    assert "shared-element continuity" in result["usefulness_reason"]

def test_element_overlap_is_scored_as_shared_element_continuity():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        [], [{"transition_type":"alkali_substitution","family":"phosphate","shared_elements":["Fe","O","P"],"preserved_framework":["Fe","O","P"],"removed_elements":["Li"],"introduced_elements":["Na"]}], "Li","Na"
    )

    breakdown = result["score_breakdown"]

    assert breakdown["shared_element_continuity"] == 30.0
    assert "framework_preservation" not in breakdown

def test_shared_element_continuity_retains_existing_weight():
    assert (
        DiscoveryPathRankingService.SHARED_ELEMENT_CONTINUITY_WEIGHT
        == 30.0
    )