from app.services.research.comparative_research_intelligence_service import (
    ComparativeResearchIntelligenceService,
)


def _opportunity(
    rank: int,
    score: float,
    quality_score: float = 12.0,
    evidence_readiness: str = "moderate",
    hop_count: int = 1,
):
    return {
        "rank": rank,
        "pathway": {
            "hop_count": hop_count,
            "materials": [],
            "transitions": [],
            "chain_reason": None,
        },
        "scientific_usefulness_score": score,
        "score_breakdown": {
            "framework_preservation": 30.0,
            "objective_alignment": 25.0,
            "transition_plausibility": 20.0,
            "path_efficiency": 10.0 if hop_count == 1 else 7.5,
            "material_quality": quality_score,
        },
        "scientific_facts": {
            "transition_types": ["alkali_substitution"],
            "preserved_framework": ["Fe", "O", "P"],
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
            "material_quality": [],
        },
        "strengths": [
            "Preserves shared framework chemistry: Fe-O-P.",
        ],
        "trade_offs": [
            "No major deterministic trade-off was identified.",
        ],
        "risks": [
            "Experimental validation is required.",
        ],
        "assumptions": [
            "Pathway ranking uses existing deterministic scoring services.",
        ],
        "confidence": {
            "level": "high" if score >= 85 else "medium",
            "reasons": [
                "Framework preservation score is strong.",
            ],
        },
        "recommended_next_investigation": (
            "Prioritize literature review, DFT validation, and property comparison."
        ),
        "researcher_decision_required": True,
        "quality_summary": {
            "average_quality_score": quality_score,
            "overall_quality": "strong" if quality_score >= 12 else "moderate",
            "highest_risk_material": "LiFePO4",
            "lowest_quality_material": "NaFePO4",
        },
        "evidence_summary": {
            "supporting_signals": [],
            "missing_evidence": [
                {
                    "statement": "Experimental synthesis evidence is unavailable.",
                    "reason": "MaterialGraph does not ingest experimental synthesis datasets.",
                    "researcher_action": "Consult experimental literature.",
                }
            ],
            "weak_assumptions": [
                {
                    "assumption": "Framework preservation may indicate related chemical behavior.",
                    "based_on": "preserved_framework transition field",
                    "requires_validation": True,
                }
            ],
            "validation_priorities": [
                {
                    "priority": 1,
                    "action": "Validate framework preservation.",
                    "reason": "Framework preservation is a major contributor.",
                }
            ],
            "evidence_readiness": evidence_readiness,
        },
    }


def test_compare_opportunities_returns_empty_comparison():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities([])

    assert result["comparison_count"] == 0
    assert result["top_ranked_pathway"] is None
    assert result["comparative_strengths"] == []
    assert result["comparative_trade_offs"] == []
    assert result["comparative_research_gaps"] == []
    assert result["comparative_assumptions"] == []
    assert result["pairwise_comparisons"] == []
    assert result["comparative_element_highlights"] == []
    assert result["researcher_decision_required"] is True


def test_compare_opportunities_identifies_top_ranked_pathway():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=82.5),
            _opportunity(rank=2, score=91.0),
        ]
    )

    assert result["comparison_count"] == 2
    assert result["top_ranked_pathway"]["rank"] == 2
    assert result["top_ranked_pathway"]["scientific_usefulness_score"] == 91.0
    assert result["top_ranked_pathway"]["why_it_ranks_highest"]


def test_compare_opportunities_preserves_strengths_tradeoffs_and_risks():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=90.0),
        ]
    )

    assert result["comparative_strengths"][0]["rank"] == 1
    assert result["comparative_strengths"][0]["strengths"]

    assert result["comparative_trade_offs"][0]["rank"] == 1
    assert result["comparative_trade_offs"][0]["trade_offs"]
    assert result["comparative_trade_offs"][0]["risks"]


def test_compare_opportunities_preserves_research_gaps_and_assumptions():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=90.0),
        ]
    )

    gaps = result["comparative_research_gaps"][0]
    assumptions = result["comparative_assumptions"][0]

    assert gaps["rank"] == 1
    assert gaps["missing_evidence"]

    assert assumptions["rank"] == 1
    assert assumptions["pathway_assumptions"]
    assert assumptions["weak_assumptions"]


def test_compare_opportunities_identifies_highest_evidence_readiness():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=91.0, evidence_readiness="moderate"),
            _opportunity(rank=2, score=86.0, evidence_readiness="strong"),
            _opportunity(rank=3, score=89.0, evidence_readiness="limited"),
        ]
    )

    evidence = result["comparative_evidence_readiness"]

    assert evidence["highest_readiness_pathway_rank"] == 2
    assert evidence["highest_readiness"] == "strong"
    assert len(evidence["pathways"]) == 3


def test_compare_opportunities_is_deterministic_for_equal_evidence_readiness():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=2, score=86.0, evidence_readiness="strong"),
            _opportunity(rank=1, score=91.0, evidence_readiness="strong"),
        ]
    )

    evidence = result["comparative_evidence_readiness"]

    assert evidence["highest_readiness_pathway_rank"] == 1


def test_compare_opportunities_does_not_recompute_or_mutate_opportunities():
    service = ComparativeResearchIntelligenceService()

    opportunities = [
        _opportunity(rank=1, score=90.0),
    ]

    original = opportunities.copy()
    original_first = opportunities[0].copy()

    service.compare_opportunities(opportunities)

    assert opportunities == original
    assert opportunities[0] == original_first

def test_compare_opportunities_returns_pairwise_comparisons():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=95.0),
            _opportunity(rank=2, score=88.0),
            _opportunity(rank=3, score=80.0),
        ]
    )

    pairwise = result["pairwise_comparisons"]

    assert len(pairwise) == 2
    assert pairwise[0]["higher_ranked_pathway_rank"] == 1
    assert pairwise[0]["lower_ranked_pathway_rank"] == 2
    assert pairwise[1]["higher_ranked_pathway_rank"] == 2
    assert pairwise[1]["lower_ranked_pathway_rank"] == 3


def test_pairwise_comparison_score_difference_is_deterministic():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=95.25),
            _opportunity(rank=2, score=88.10),
        ]
    )

    pair = result["pairwise_comparisons"][0]

    assert pair["score_difference"] == 7.15


def test_pairwise_comparison_explains_higher_ranked_score_dimensions():
    service = ComparativeResearchIntelligenceService()

    higher = _opportunity(rank=1, score=95.0)
    lower = _opportunity(rank=2, score=88.0)

    higher["score_breakdown"] = {
        "framework_preservation": 30.0,
        "objective_alignment": 25.0,
        "transition_plausibility": 20.0,
        "path_efficiency": 10.0,
        "material_quality": 10.0,
    }

    lower["score_breakdown"] = {
        "framework_preservation": 20.0,
        "objective_alignment": 25.0,
        "transition_plausibility": 15.0,
        "path_efficiency": 7.5,
        "material_quality": 20.0,
    }

    result = service.compare_opportunities([higher, lower])

    reasons = result["pairwise_comparisons"][0]["why_higher_ranked"]
    dimensions = {reason["dimension"] for reason in reasons}

    assert "framework_preservation" in dimensions
    assert "transition_plausibility" in dimensions
    assert "path_efficiency" in dimensions

    framework_reason = next(
        reason
        for reason in reasons
        if reason["dimension"] == "framework_preservation"
    )

    assert framework_reason["higher_score"] == 30.0
    assert framework_reason["lower_score"] == 20.0
    assert framework_reason["difference"] == 10.0
    assert framework_reason["explanation"]


def test_pairwise_comparison_preserves_lower_ranked_advantages():
    service = ComparativeResearchIntelligenceService()

    higher = _opportunity(rank=1, score=95.0)
    lower = _opportunity(rank=2, score=88.0)

    higher["score_breakdown"] = {
        "framework_preservation": 30.0,
        "objective_alignment": 25.0,
        "transition_plausibility": 20.0,
        "path_efficiency": 10.0,
        "material_quality": 8.0,
    }

    lower["score_breakdown"] = {
        "framework_preservation": 25.0,
        "objective_alignment": 20.0,
        "transition_plausibility": 15.0,
        "path_efficiency": 7.5,
        "material_quality": 12.0,
    }

    result = service.compare_opportunities([higher, lower])

    advantages = result["pairwise_comparisons"][0][
        "lower_ranked_pathway_advantages"
    ]

    assert len(advantages) == 1
    assert advantages[0]["dimension"] == "material_quality"
    assert advantages[0]["higher_ranked_score"] == 8.0
    assert advantages[0]["lower_ranked_score"] == 12.0
    assert advantages[0]["difference"] == 4.0
    assert advantages[0]["explanation"]


def test_pairwise_comparison_includes_evidence_readiness_difference():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=95.0, evidence_readiness="moderate"),
            _opportunity(rank=2, score=88.0, evidence_readiness="strong"),
        ]
    )

    evidence = result["pairwise_comparisons"][0][
        "evidence_readiness_comparison"
    ]

    assert evidence["higher_ranked_pathway_readiness"] == "moderate"
    assert evidence["lower_ranked_pathway_readiness"] == "strong"
    assert evidence["same_readiness"] is False
   
def test_comparative_element_highlights_include_introduced_elements():
    service = ComparativeResearchIntelligenceService()

    opportunity = _opportunity(rank=1, score=95.0)
    opportunity["scientific_facts"]["introduced_elements"] = ["Na"]

    result = service.compare_opportunities([opportunity])

    highlights = result["comparative_element_highlights"]

    na_highlight = next(
        item
        for item in highlights
        if item["element"] == "Na"
        and item["role"] == "introduced_element"
    )

    assert na_highlight["appears_in_pathway_ranks"] == [1]
    assert "Na" in na_highlight["potential_signal"]
    assert "introducing Na" in na_highlight["researcher_action"]
    assert na_highlight["requires_validation"] is True


def test_comparative_element_highlights_include_preserved_framework_elements():
    service = ComparativeResearchIntelligenceService()

    opportunity = _opportunity(rank=1, score=95.0)
    opportunity["scientific_facts"]["preserved_framework"] = ["Fe", "O", "P"]

    result = service.compare_opportunities([opportunity])

    highlights = result["comparative_element_highlights"]

    fe_highlight = next(
        item
        for item in highlights
        if item["element"] == "Fe"
        and item["role"] == "preserved_framework"
    )

    assert fe_highlight["appears_in_pathway_ranks"] == [1]
    assert "Fe" in fe_highlight["potential_signal"]
    assert "Fe-containing framework chemistry" in fe_highlight["researcher_action"]
    assert fe_highlight["requires_validation"] is True


def test_comparative_element_highlights_include_removed_elements():
    service = ComparativeResearchIntelligenceService()

    opportunity = _opportunity(rank=1, score=95.0)
    opportunity["scientific_facts"]["removed_elements"] = ["Li"]

    result = service.compare_opportunities([opportunity])

    highlights = result["comparative_element_highlights"]

    li_highlight = next(
        item
        for item in highlights
        if item["element"] == "Li"
        and item["role"] == "removed_element"
    )

    assert li_highlight["appears_in_pathway_ranks"] == [1]
    assert "Li" in li_highlight["potential_signal"]
    assert "removing or avoiding Li" in li_highlight["researcher_action"]
    assert li_highlight["requires_validation"] is True


def test_comparative_element_highlights_group_repeated_elements_across_pathways():
    service = ComparativeResearchIntelligenceService()

    first = _opportunity(rank=1, score=95.0)
    second = _opportunity(rank=2, score=88.0)

    first["scientific_facts"]["introduced_elements"] = ["Na"]
    second["scientific_facts"]["introduced_elements"] = ["Na"]

    result = service.compare_opportunities([first, second])

    highlights = result["comparative_element_highlights"]

    na_highlight = next(
        item
        for item in highlights
        if item["element"] == "Na"
        and item["role"] == "introduced_element"
    )

    assert na_highlight["appears_in_pathway_ranks"] == [1, 2]


def test_all_comparative_element_highlights_require_validation():
    service = ComparativeResearchIntelligenceService()

    opportunity = _opportunity(rank=1, score=95.0)
    opportunity["scientific_facts"]["introduced_elements"] = ["Na"]
    opportunity["scientific_facts"]["removed_elements"] = ["Li"]
    opportunity["scientific_facts"]["preserved_framework"] = ["Fe", "O", "P"]

    result = service.compare_opportunities([opportunity])

    highlights = result["comparative_element_highlights"]

    assert highlights
    assert all(
        item["requires_validation"] is True
        for item in highlights
    )

def test_pairwise_comparison_marks_equal_scores_as_tie():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=94.95),
            _opportunity(rank=2, score=94.95),
        ]
    )

    pair = result["pairwise_comparisons"][0]

    assert pair["comparison_type"] == "tie"
    assert pair["score_difference"] == 0
    assert pair["tie_reason"]


def test_pairwise_comparison_includes_endpoint_material_comparison():
    service = ComparativeResearchIntelligenceService()

    first = _opportunity(rank=1, score=94.95)
    second = _opportunity(rank=2, score=94.95)

    first["pathway"]["materials"] = [
        {"material_id": 5, "formula": "LiFePO4", "pretty_formula": "LiFePO4", "mp_id": "mp-19017"},
        {"material_id": 7, "formula": "Na3Fe3(PO4)4", "pretty_formula": "Na3Fe3(PO4)4", "mp_id": "mp-556540"},
    ]

    second["pathway"]["materials"] = [
        {"material_id": 5, "formula": "LiFePO4", "pretty_formula": "LiFePO4", "mp_id": "mp-19017"},
        {"material_id": 10, "formula": "NaFePO4", "pretty_formula": "NaFePO4", "mp_id": "mp-19226"},
    ]

    result = service.compare_opportunities([first, second])

    endpoint_comparison = result["pairwise_comparisons"][0][
        "endpoint_material_comparison"
    ]

    assert endpoint_comparison["same_endpoint"] is False
    assert endpoint_comparison["first_pathway_endpoint"]["material_id"] == 7
    assert endpoint_comparison["second_pathway_endpoint"]["material_id"] == 10

    # Backward-compatible aliases
    assert endpoint_comparison["higher_ranked_endpoint"]["material_id"] == 7
    assert endpoint_comparison["lower_ranked_endpoint"]["material_id"] == 10

def test_pairwise_comparison_includes_neutral_rank_aliases():
    service = ComparativeResearchIntelligenceService()

    result = service.compare_opportunities(
        [
            _opportunity(rank=1, score=94.95),
            _opportunity(rank=2, score=94.95),
        ]
    )

    pair = result["pairwise_comparisons"][0]

    assert pair["first_pathway_rank"] == 1
    assert pair["second_pathway_rank"] == 2
    assert pair["higher_ranked_pathway_rank"] == 1
    assert pair["lower_ranked_pathway_rank"] == 2