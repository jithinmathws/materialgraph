from app.services.research.research_evidence_intelligence_service import (
    ResearchEvidenceIntelligenceService,
)


def _sample_opportunity() -> dict:
    return {
        "score_breakdown": {
            "framework_preservation": 30.0,
            "objective_alignment": 25.0,
            "transition_plausibility": 18.5,
            "path_efficiency": 7.5,
            "material_quality": 13.95,
        },
        "scientific_facts": {
            "transition_types": ["alkali_substitution", "family_expansion"],
            "preserved_framework": ["Fe", "O", "P"],
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
            "material_quality": [
                {
                    "material_id": 5,
                    "stability_score": 100.0,
                    "energy_above_hull": 0.0,
                    "criticality_score": 36.5,
                    "risk_score": 2.833,
                    "quality_score": 13.95,
                }
            ],
        },
        "quality_summary": {
            "average_quality_score": 13.95,
            "overall_quality": "strong",
            "highest_risk_material": "LiFePO4",
            "lowest_quality_material": "LiFePO4",
        },
    }


def test_research_evidence_summary_contains_required_sections():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assert "supporting_signals" in evidence
    assert "missing_evidence" in evidence
    assert "weak_assumptions" in evidence
    assert "validation_priorities" in evidence
    assert "evidence_readiness" in evidence


def test_supporting_signals_are_attributed():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    signal = evidence["supporting_signals"][0]

    assert "statement" in signal
    assert "source_service" in signal
    assert "derived_from" in signal
    assert "confidence" in signal


def test_missing_evidence_is_explainable():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary({})

    missing = evidence["missing_evidence"][0]

    assert "statement" in missing
    assert "reason" in missing
    assert "researcher_action" in missing

    assert any(
        "Experimental synthesis evidence" in item["statement"]
        for item in evidence["missing_evidence"]
    )

    assert any(
        "Scientific literature support" in item["statement"]
        for item in evidence["missing_evidence"]
    )


def test_weak_assumptions_are_structured():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assumption = evidence["weak_assumptions"][0]

    assert "assumption" in assumption
    assert "based_on" in assumption
    assert "requires_validation" in assumption


def test_validation_priorities_are_structured():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    priority = evidence["validation_priorities"][0]

    assert "priority" in priority
    assert "action" in priority
    assert "reason" in priority


def test_research_evidence_readiness_is_valid():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assert evidence["evidence_readiness"] in {
        "limited",
        "moderate",
        "strong",
    }


def test_enrich_opportunity_adds_evidence_summary():
    service = ResearchEvidenceIntelligenceService()

    opportunity = {
        "rank": 1,
        "score_breakdown": {},
        "scientific_facts": {},
        "quality_summary": {},
    }

    enriched = service.enrich_opportunity(opportunity)

    assert "evidence_summary" in enriched
    assert enriched["rank"] == 1