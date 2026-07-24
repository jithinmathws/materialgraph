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
    assert evidence["evidence_readiness"] in {
        "limited",
        "moderate",
        "strong",
    }
    
    assert "objective_satisfaction" in opportunity

    objective_satisfaction = opportunity["objective_satisfaction"]

    assert "matched_avoid_elements" in objective_satisfaction
    assert "unmatched_avoid_elements" in objective_satisfaction
    assert "matched_prefer_elements" in objective_satisfaction
    assert "unmatched_prefer_elements" in objective_satisfaction
    assert objective_satisfaction["status"] in {
        "complete",
        "partial",
        "unmatched",
    }

    signal = evidence["supporting_signals"][0]
    assert "statement" in signal
    assert "source_service" in signal
    assert "derived_from" in signal
    assert "confidence" in signal

    missing = evidence["missing_evidence"][0]
    assert "statement" in missing
    assert "reason" in missing
    assert "researcher_action" in missing

    assumption = evidence["weak_assumptions"][0]
    assert "assumption" in assumption
    assert "based_on" in assumption
    assert "requires_validation" in assumption

    priority = evidence["validation_priorities"][0]
    assert "priority" in priority
    assert "action" in priority
    assert "reason" in priority


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


def test_scientific_pathway_analysis_exposes_complete_objective_satisfaction(
    db_session,
):
    from app.schemas.discovery import ResearchObjective
    from app.services.research.scientific_pathway_analysis_service import (
        ScientificPathwayAnalysisService,
    )

    service = ScientificPathwayAnalysisService(db_session)

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

    satisfaction = result["pathway_opportunities"][0][
        "objective_satisfaction"
    ]

    assert satisfaction == {
        "requested_avoid_elements": ["Li"],
        "matched_avoid_elements": ["Li"],
        "unmatched_avoid_elements": [],
        "requested_prefer_elements": ["Na"],
        "matched_prefer_elements": ["Na"],
        "unmatched_prefer_elements": [],
        "avoid_coverage": 1.0,
        "prefer_coverage": 1.0,
        "overall_coverage": 1.0,
        "status": "complete",
        "interpretation": (
            "All requested avoid and prefer element objectives are "
            "represented by path-wide removal and introduction events."
        ),
        "endpoint_matched_avoid_elements": ["Li"],
        "endpoint_unmatched_avoid_elements": [],
        "endpoint_matched_prefer_elements": ["Na"],
        "endpoint_unmatched_prefer_elements": [],
        "endpoint_avoid_coverage": 1.0,
        "endpoint_prefer_coverage": 1.0,
        "endpoint_overall_coverage": 1.0,
        "endpoint_status": "complete",
        "endpoint_interpretation": (
            "The final endpoint material satisfies all requested avoid "
            "and prefer element objectives."
        ),
    }


def test_scientific_pathway_analysis_exposes_partial_objective_satisfaction(
    db_session,
):
    from app.schemas.discovery import ResearchObjective
    from app.services.research.scientific_pathway_analysis_service import (
        ScientificPathwayAnalysisService,
    )

    service = ScientificPathwayAnalysisService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
        prefer_lower_criticality=True,
        require_stable_materials=False,
    )

    result = service.analyze(material_id=5, objective=objective)

    opportunity = result["pathway_opportunities"][0]
    satisfaction = opportunity["objective_satisfaction"]

    assert satisfaction["requested_avoid_elements"] == ["Co", "Li"]
    assert satisfaction["matched_avoid_elements"] == ["Li"]
    assert satisfaction["unmatched_avoid_elements"] == ["Co"]

    assert satisfaction["requested_prefer_elements"] == ["K", "Na"]
    assert satisfaction["matched_prefer_elements"] == ["Na"]
    assert satisfaction["unmatched_prefer_elements"] == ["K"]

    assert satisfaction["avoid_coverage"] == 0.5
    assert satisfaction["prefer_coverage"] == 0.5
    assert satisfaction["overall_coverage"] == 0.5
    assert satisfaction["status"] == "partial"

    # Path-event coverage remains partial, while ranking uses the
    # final material's endpoint composition.
    assert opportunity["score_breakdown"]["objective_alignment"] == 18.75
    assert opportunity["scientific_usefulness_score"] == 89.4


def test_scientific_pathway_analysis_assigns_unique_pathway_identity(
    db_session,
):
    from app.schemas.discovery import ResearchObjective

    service = ScientificPathwayAnalysisService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.analyze(
        material_id=5,
        objective=objective,
    )

    opportunities = result["pathway_opportunities"]

    assert opportunities

    pathway_ids = []
    positions = []

    for expected_position, opportunity in enumerate(
        opportunities,
        start=1,
    ):
        assert opportunity["position"] == expected_position

        material_ids = [
            material["material_id"]
            for material in opportunity["pathway"]["materials"]
        ]

        expected_pathway_id = (
            "pathway:"
            + "-".join(str(item) for item in material_ids)
        )

        assert opportunity["pathway_id"] == expected_pathway_id

        pathway_ids.append(opportunity["pathway_id"])
        positions.append(opportunity["position"])

    assert len(pathway_ids) == len(set(pathway_ids))
    assert len(positions) == len(set(positions))
    

def test_objective_satisfaction_is_element_order_independent():
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    first = service._build_objective_satisfaction(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        removed_elements=["Li"],
        introduced_elements=["Na"],
    )
    second = service._build_objective_satisfaction(
        avoid_elements=["Co", "Li"],
        prefer_elements=["K", "Na"],
        removed_elements=["Li"],
        introduced_elements=["Na"],
    )

    assert first == second


def test_objective_satisfaction_handles_empty_objectives():
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    result = service._build_objective_satisfaction(
        avoid_elements=[],
        prefer_elements=[],
        removed_elements=["Li"],
        introduced_elements=["Na"],
    )

    assert result["avoid_coverage"] == 1.0
    assert result["prefer_coverage"] == 1.0
    assert result["overall_coverage"] == 1.0
    assert result["status"] == "complete"

def test_endpoint_objective_satisfaction_uses_final_composition_only():
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    result = service._build_endpoint_objective_satisfaction(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        endpoint_elements=["Na", "Fe", "P", "O"],
    )

    assert result == {
        "endpoint_matched_avoid_elements": ["Co", "Li"],
        "endpoint_unmatched_avoid_elements": [],
        "endpoint_matched_prefer_elements": ["Na"],
        "endpoint_unmatched_prefer_elements": ["K"],
        "endpoint_avoid_coverage": 1.0,
        "endpoint_prefer_coverage": 0.5,
        "endpoint_overall_coverage": 0.75,
        "endpoint_status": "partial",
        "endpoint_interpretation": (
            "The final endpoint material satisfies some requested avoid "
            "or prefer element objectives; unmatched endpoint objectives remain."
        ),
    }


def test_path_and_endpoint_satisfaction_can_differ():
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    path = service._build_objective_satisfaction(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        removed_elements=["Li"],
        introduced_elements=["Na"],
    )
    endpoint = service._build_endpoint_objective_satisfaction(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        endpoint_elements=["Li", "Na", "Fe", "P", "O"],
    )

    assert path["status"] == "complete"
    assert path["matched_avoid_elements"] == ["Li"]

    assert endpoint["endpoint_status"] == "partial"
    assert endpoint["endpoint_unmatched_avoid_elements"] == ["Li"]
    assert endpoint["endpoint_matched_prefer_elements"] == ["Na"]


def test_endpoint_element_extraction_uses_exact_formula_elements():
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    elements = service._endpoint_elements(
        [{"formula": "NaFePO4", "pretty_formula": "NaFePO4"}]
    )

    assert elements == ["Fe", "Na", "O", "P"]
    assert "N" not in elements


def test_endpoint_objective_satisfaction_handles_empty_objectives():
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    result = service._build_endpoint_objective_satisfaction(
        avoid_elements=[],
        prefer_elements=[],
        endpoint_elements=["Na", "Fe", "P", "O"],
    )

    assert result["endpoint_avoid_coverage"] == 1.0
    assert result["endpoint_prefer_coverage"] == 1.0
    assert result["endpoint_overall_coverage"] == 1.0
    assert result["endpoint_status"] == "complete"


def test_common_shared_elements_uses_path_wide_intersection(
    db_session,
):
    service = ScientificPathwayAnalysisService(db_session)

    transitions = [
        {"shared_elements": ["Fe", "P"]},
        {"shared_elements": ["Fe", "O"]},
    ]

    assert service._common_shared_elements(transitions) == ["Fe"]


def test_common_shared_elements_requires_evidence_from_every_transition(
    db_session,
):
    service = ScientificPathwayAnalysisService(db_session)

    transitions = [
        {"shared_elements": ["Fe", "P", "O"]},
        {},
    ]

    assert service._common_shared_elements(transitions) == []


def test_common_shared_elements_supports_compatibility_alias(
    db_session,
):
    service = ScientificPathwayAnalysisService(db_session)

    transitions = [
        {"preserved_framework": ["Fe", "P", "O"]},
        {"preserved_framework": ["Fe", "O"]},
    ]

    assert service._common_shared_elements(transitions) == ["Fe", "O"]


def test_common_shared_elements_prefers_primary_field(
    db_session,
):
    service = ScientificPathwayAnalysisService(db_session)

    transitions = [
        {
            "shared_elements": [],
            "preserved_framework": ["Fe", "P", "O"],
        },
    ]

    assert service._common_shared_elements(transitions) == []