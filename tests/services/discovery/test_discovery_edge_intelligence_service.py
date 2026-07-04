from app.services.discovery.edge_intelligence_service import (
    DiscoveryEdgeIntelligenceService,
)

def test_edge_intelligence_scores_alkali_substitution():
    service = DiscoveryEdgeIntelligenceService()

    result = service.build_edge_intelligence(
        transition_type="alkali_substitution",
        family="phosphate",
        preserved_framework=["Fe", "P", "O"],
        removed_elements=["Li"],
        introduced_elements=["Na"],
        scientific_reason="Li is replaced by Na while preserving phosphate chemistry.",
    )

    assert result["scientific_plausibility"] == 1.0
    assert result["edge_score"] == 100.0
    assert "scientific_reason" in result


def test_edge_intelligence_scores_family_expansion():
    service = DiscoveryEdgeIntelligenceService()

    result = service.build_edge_intelligence(
        transition_type="family_expansion",
        family="phosphate",
        preserved_framework=["P", "O"],
        removed_elements=[],
        introduced_elements=[],
        scientific_reason="Expands within phosphate family.",
    )

    assert result["scientific_plausibility"] == 0.75
    assert result["edge_score"] == 90.0


def test_edge_intelligence_scores_unknown_transition():
    service = DiscoveryEdgeIntelligenceService()

    result = service.build_edge_intelligence(
        transition_type=None,
        family=None,
        preserved_framework=[],
        removed_elements=[],
        introduced_elements=[],
        scientific_reason="Fallback transition.",
    )

    assert result["scientific_plausibility"] == 0.5
    assert result["edge_score"] == 50.0