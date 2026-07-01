from app.services.research.scientific_pathway_analysis_service import (
    ScientificPathwayAnalysisService,
)


def test_scientific_pathway_analysis_returns_opportunities(db_session):
    service = ScientificPathwayAnalysisService(db_session)

    from app.schemas.discovery import ResearchObjective

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
        prefer_lower_criticality=True,
        require_stable_materials=False,
    )

    result = service.analyze(material_id=5, objective=objective)

    assert result["material_id"] == 5
    assert result["researcher_decision_required"] is True
    assert "pathway_opportunities" in result
    assert "pathway_comparison" in result

    assert len(result["pathway_opportunities"]) > 0

    opportunity = result["pathway_opportunities"][0]

    assert opportunity["researcher_decision_required"] is True
    assert "pathway" in opportunity
    assert "scientific_facts" in opportunity
    assert "quality_summary" in opportunity
    assert "confidence" in opportunity
    assert "recommended_next_investigation" in opportunity

    assert "evidence_summary" in opportunity

    evidence = opportunity["evidence_summary"]

    assert "supporting_signals" in evidence
    assert "missing_evidence" in evidence
    assert "weak_assumptions" in evidence
    assert "validation_priorities" in evidence
    assert evidence["evidence_confidence"] in {
        "limited",
        "moderate",
        "strong",
    }


def test_scientific_pathway_analysis_confidence_is_explainable(db_session):
    service = ScientificPathwayAnalysisService(db_session)

    from app.schemas.discovery import ResearchObjective

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.analyze(material_id=5, objective=objective)

    opportunity = result["pathway_opportunities"][0]
    confidence = opportunity["confidence"]

    assert confidence["level"] in {"high", "medium", "low"}
    assert isinstance(confidence["reasons"], list)
    assert len(confidence["reasons"]) > 0


def test_scientific_pathway_analysis_quality_summary_exists(db_session):
    service = ScientificPathwayAnalysisService(db_session)

    from app.schemas.discovery import ResearchObjective

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.analyze(material_id=5, objective=objective)

    opportunity = result["pathway_opportunities"][0]
    quality_summary = opportunity["quality_summary"]

    assert "average_quality_score" in quality_summary
    assert "overall_quality" in quality_summary
    assert quality_summary["overall_quality"] in {
        "strong",
        "moderate",
        "weak",
        "unknown",
    }


def test_scientific_pathway_analysis_empty_material_is_safe(db_session):
    service = ScientificPathwayAnalysisService(db_session)

    from app.schemas.discovery import ResearchObjective

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.analyze(material_id=999999, objective=objective)

    assert result["material_id"] == 999999
    assert result["base_formula"] is None
    assert result["pathway_opportunities"] == []
    assert result["researcher_decision_required"] is True