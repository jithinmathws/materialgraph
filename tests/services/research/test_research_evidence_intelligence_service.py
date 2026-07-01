from app.services.research.research_evidence_intelligence_service import (
    ResearchEvidenceIntelligenceService,
)


def test_research_evidence_summary_contains_required_sections():
    service = ResearchEvidenceIntelligenceService()

    opportunity = {
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

    evidence = service.build_evidence_summary(opportunity)

    assert "supporting_signals" in evidence
    assert "missing_evidence" in evidence
    assert "weak_assumptions" in evidence
    assert "validation_priorities" in evidence
    assert "evidence_confidence" in evidence


def test_research_evidence_summary_has_missing_evidence():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary({})

    assert any(
        "Experimental synthesis evidence" in item
        for item in evidence["missing_evidence"]
    )
    assert any(
        "Scientific literature support" in item
        for item in evidence["missing_evidence"]
    )


def test_research_evidence_confidence_is_valid():
    service = ResearchEvidenceIntelligenceService()

    opportunity = {
        "score_breakdown": {
            "framework_preservation": 30.0,
            "objective_alignment": 25.0,
            "transition_plausibility": 18.5,
        },
        "scientific_facts": {
            "preserved_framework": ["Fe", "O", "P"],
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
            "material_quality": [],
        },
        "quality_summary": {
            "average_quality_score": 13.95,
            "overall_quality": "strong",
        },
    }

    evidence = service.build_evidence_summary(opportunity)

    assert evidence["evidence_confidence"] in {
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