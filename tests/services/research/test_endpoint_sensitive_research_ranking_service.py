from app.services.research.endpoint_sensitive_research_ranking_service import (
    EndpointSensitiveResearchRankingService,
)


def _opportunity(rank, endpoint_id, formula, quality_score=13.95, risk_score=1.5):
    return {
        "rank": rank,
        "scientific_usefulness_score": 94.95,
        "pathway": {
            "materials": [
                {"material_id": 5, "formula": "LiFePO4", "pretty_formula": "LiFePO4"},
                {"material_id": endpoint_id, "formula": formula, "pretty_formula": formula},
            ]
        },
        "scientific_facts": {
            "material_quality": [
                {
                    "material_id": endpoint_id,
                    "quality_score": quality_score,
                    "stability_score": 100.0,
                    "energy_above_hull": 0.0,
                    "criticality_score": 31.0,
                    "risk_score": risk_score,
                }
            ]
        },
        "evidence_summary": {"evidence_readiness": "strong"},
    }


def test_endpoint_sensitive_ranking_preserves_identical_endpoint_evidence_tie():
    service = EndpointSensitiveResearchRankingService()

    result = service.rank_opportunities([
        _opportunity(1, 7, "Na3Fe3(PO4)4"),
        _opportunity(2, 8, "Na9Fe3P8O29"),
    ])

    assert result["score_preserved"] is True
    assert result["endpoint_sensitive_score_added"] is False
    assert result["differentiated_group_count"] == 0
    assert result["preserved_tie_group_count"] == 1
    assert result["groups"][0]["differentiation_status"] == "tie_preserved"
    assert result["groups"][0]["tie_preserved"] is True


def test_endpoint_sensitive_ranking_differentiates_when_endpoint_quality_differs():
    service = EndpointSensitiveResearchRankingService()

    result = service.rank_opportunities([
        _opportunity(1, 7, "Na3Fe3(PO4)4", quality_score=12.5),
        _opportunity(2, 8, "Na9Fe3P8O29", quality_score=14.0),
    ])

    group = result["groups"][0]
    first_priority_group = group["endpoint_priority_groups"][0]

    assert result["differentiated_group_count"] == 1
    assert group["differentiation_status"] == "endpoint_differentiated"
    assert first_priority_group["pathways"][0]["pathway_rank"] == 2
    assert first_priority_group["shared_endpoint_evidence"]["endpoint_quality_score"] == 14.0


def test_endpoint_sensitive_ranking_preserves_tie_when_endpoint_quality_missing():
    service = EndpointSensitiveResearchRankingService()

    opportunity_a = _opportunity(1, 7, "Na3Fe3(PO4)4")
    opportunity_b = _opportunity(2, 8, "Na9Fe3P8O29")
    opportunity_a["scientific_facts"] = {"material_quality": []}
    opportunity_b["scientific_facts"] = {"material_quality": []}

    result = service.rank_opportunities([opportunity_a, opportunity_b])

    assert result["differentiated_group_count"] == 0
    assert result["preserved_tie_group_count"] == 1
    assert result["groups"][0]["differentiation_status"] == "tie_preserved"


def test_endpoint_sensitive_ranking_never_changes_scientific_usefulness_score():
    service = EndpointSensitiveResearchRankingService()
    opportunities = [
        _opportunity(1, 7, "Na3Fe3(PO4)4", quality_score=12.5),
        _opportunity(2, 8, "Na9Fe3P8O29", quality_score=14.0),
    ]

    before_scores = [item["scientific_usefulness_score"] for item in opportunities]
    service.rank_opportunities(opportunities)
    after_scores = [item["scientific_usefulness_score"] for item in opportunities]

    assert after_scores == before_scores
