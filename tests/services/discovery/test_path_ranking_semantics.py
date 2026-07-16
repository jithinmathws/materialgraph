from app.services.discovery.path_ranking_service import DiscoveryPathRankingService

def test_path_ranking_preserves_scores_but_qualifies_reason():
    result=DiscoveryPathRankingService().rank_path([], [{"transition_type":"alkali_substitution","family":"phosphate","shared_elements":["Fe","O","P"],"preserved_framework":["Fe","O","P"],"removed_elements":["Li"],"introduced_elements":["Na"]}], "Li","Na")
    assert result["scientific_usefulness_score"]==85.0
    assert result["score_breakdown"]["framework_preservation"]==30.0
    assert "shared-element continuity" in result["usefulness_reason"]
