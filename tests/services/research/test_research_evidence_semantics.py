from app.services.research.research_evidence_intelligence_service import ResearchEvidenceIntelligenceService

def test_evidence_qualifies_element_overlap_and_structural_uncertainty():
    evidence = ResearchEvidenceIntelligenceService().build_evidence_summary(
        {
            "score_breakdown": {
                "shared_element_continuity": 30.0,
                "objective_alignment": 25.0,
                "transition_plausibility": 18.5,
                "path_efficiency": 7.5,
                "material_quality": 14.0,
            },
            "scientific_facts": {
                "shared_elements": ["Fe", "O", "P"],
                "preserved_framework": ["Fe", "O", "P"],
            },
            "quality_summary": {
                "average_quality_score": 14.0,
                "overall_quality": "strong",
            },
        }
    )
    signals = evidence["supporting_signals"]

    continuity_signal = next(
        signal
        for signal in signals
        if signal["derived_from"] == "shared_element_continuity"
    )

    assert continuity_signal["confidence"] == "moderate"
    assert "Shared-element continuity" in continuity_signal["statement"]
    overlap_signal = next(
        signal
        for signal in signals
        if signal["derived_from"] == "element_overlap"
    )

    assert overlap_signal["confidence"] == "moderate"
    assert (
        "Structural preservation is not validated"
        in overlap_signal["statement"]
    )
