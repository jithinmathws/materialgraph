from app.services.research.comparative_research_intelligence_service import (
    ComparativeResearchIntelligenceService,
)


def test_comparative_highlights_use_shared_element_semantics():
    opportunity = {
        "pathway_id": "pathway:5-7",
        "position": 1,
        "rank": 1,
        "pathway": {
            "materials": [],
            "transitions": [],
        },
        "scientific_usefulness_score": 90.0,
        "score_breakdown": {},
        "scientific_facts": {
            "shared_elements": ["Fe"],
            "preserved_framework": ["Fe"],
            "introduced_elements": [],
            "removed_elements": [],
        },
        "strengths": [],
        "trade_offs": [],
        "risks": [],
        "assumptions": [],
        "evidence_summary": {
            "missing_evidence": [],
            "weak_assumptions": [],
            "evidence_readiness": "moderate",
        },
    }

    result = (
        ComparativeResearchIntelligenceService()
        .compare_opportunities([opportunity])
    )

    highlights = result["comparative_element_highlights"]

    assert len(highlights) == 1

    highlight = highlights[0]

    assert highlight["element"] == "Fe"
    assert highlight["role"] == "preserved_framework"
    assert highlight["role_semantics"] == "element_overlap"
    assert highlight["structural_preservation_validated"] is False

    assert highlight["pathway_ids"] == ["pathway:5-7"]
    assert highlight["pathway_count"] == 1
    assert highlight["appears_in_pathway_ranks"] == [1]

    assert highlight["requires_validation"] is True