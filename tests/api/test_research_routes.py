def test_scientific_pathway_analysis_returns_comparative_intelligence(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    comparison = data["pathway_comparison"]

    assert comparison["comparison_count"] == len(
        data["pathway_opportunities"]
    )

    assert "top_ranked_pathway" in comparison
    assert "comparative_strengths" in comparison
    assert "comparative_trade_offs" in comparison
    assert "comparative_research_gaps" in comparison
    assert "comparative_evidence_readiness" in comparison
    assert "comparative_assumptions" in comparison

    assert comparison["researcher_decision_required"] is True
    assert comparison["decision_boundary"]

def test_scientific_pathway_comparison_top_rank_matches_highest_score(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    opportunities = data["pathway_opportunities"]
    comparison = data["pathway_comparison"]

    if not opportunities:
        assert comparison["top_ranked_pathway"] is None
        return

    expected_top = max(
        opportunities,
        key=lambda item: item["scientific_usefulness_score"],
    )

    assert comparison["top_ranked_pathway"]["rank"] == expected_top["rank"]

    assert (
        comparison["top_ranked_pathway"]["scientific_usefulness_score"]
        == expected_top["scientific_usefulness_score"]
    )

def test_scientific_pathway_comparison_preserves_researcher_autonomy(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    comparison = response.json()["pathway_comparison"]

    assert comparison["researcher_decision_required"] is True

    decision_boundary = comparison["decision_boundary"].lower()

    assert "researchers remain responsible" in decision_boundary
    assert "validation" in decision_boundary

def test_scientific_pathway_analysis_returns_pairwise_comparisons(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    opportunities = data["pathway_opportunities"]
    pairwise = data["pathway_comparison"]["pairwise_comparisons"]

    expected_count = max(len(opportunities) - 1, 0)

    assert len(pairwise) == expected_count

    if len(opportunities) < 2:
        return

    first = pairwise[0]

    assert "higher_ranked_pathway_rank" in first
    assert "lower_ranked_pathway_rank" in first
    assert "score_difference" in first
    assert "why_higher_ranked" in first
    assert "lower_ranked_pathway_advantages" in first
    assert "evidence_readiness_comparison" in first
    
    assert "comparison_type" in first
    assert "tie_reason" in first
    assert "endpoint_material_comparison" in first

    assert first["score_difference"] >= 0

def test_scientific_pathway_analysis_returns_comparative_element_highlights(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    highlights = data["pathway_comparison"][
        "comparative_element_highlights"
    ]

    assert isinstance(highlights, list)

    for highlight in highlights:
        assert "element" in highlight
        assert "role" in highlight
        assert "appears_in_pathway_ranks" in highlight
        assert "potential_signal" in highlight
        assert "researcher_action" in highlight
        assert highlight["requires_validation"] is True

def test_comparative_element_highlights_are_grounded_in_pathway_facts(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    opportunities = data["pathway_opportunities"]
    highlights = data["pathway_comparison"][
        "comparative_element_highlights"
    ]

    role_to_fact_key = {
        "introduced_element": "introduced_elements",
        "removed_element": "removed_elements",
        "preserved_framework": "preserved_framework",
    }

    for highlight in highlights:
        fact_key = role_to_fact_key[highlight["role"]]

        grounded_ranks = {
            opportunity["rank"]
            for opportunity in opportunities
            if highlight["element"]
            in opportunity["scientific_facts"].get(fact_key, [])
        }

        assert grounded_ranks == set(
            highlight["appears_in_pathway_ranks"]
        )